import pytest
from plenum.common.keygen_utils import initRemoteKeys
from plenum.common.util import getMaxFailures

from stp_core.loop.eventually import eventually
from plenum.common.exceptions import MissingSignature
from plenum.common.exceptions import NotConnectedToAny
from stp_core.common.log import getlogger
from plenum.common.constants import OP_FIELD_NAME, REPLY, REQACK
from plenum.common.types import f
from plenum.server.node import Node
from plenum.test import waits
from plenum.test.helper import checkResponseCorrectnessFromNodes, \
    randomOperation, checkLastClientReqForNode, getRepliesFromClientInbox, \
    sendRandomRequest, waitForSufficientRepliesForRequests, assertLength, \
    sendReqsToNodesAndVerifySuffReplies

from plenum.test.test_client import genTestClient

nodeCount = 7

F = getMaxFailures(nodeCount)

whitelist = ['signer not configured so not signing',
             'for EmptySignature',
             'discarding message',
             'found legacy entry',
             'public key from disk',
             'verification key from disk',
             'got error while verifying message']  # warnings

logger = getlogger()


def checkResponseRecvdFromNodes(client, expectedCount: int,
                                expectedReqId: int):
    # Checks if the client has unique `expectedCount` number of REQACKs and
    # REPLYs from nodes. It ignores more than one REQACK or REPLY since a
    # client might be retrying
    acks = set()
    replies = set()
    for (resp, nodeNm) in client.inBox:
        op = resp.get(OP_FIELD_NAME)
        if op == REPLY:
            reqId = resp.get(f.RESULT.nm, {}).get(f.REQ_ID.nm)
            coll = replies
        elif op == REQACK:
            reqId = resp.get(f.REQ_ID.nm)
            coll = acks
        else:
            continue
        if reqId == expectedReqId:
            coll.add(nodeNm)
    assert len(replies) == len(acks) == expectedCount


# noinspection PyIncorrectDocstring
def testClientShouldNotBeAbleToConnectToNodesNodeStack(pool):
    """
    Client should not be able to connect to nodes in the node's nodestack
    """

    async def go(ctx):
        nodestacksVersion = {k: v.ha for k, v in ctx.nodeset.nodeReg.items()}
        client1, _ = genTestClient(
            nodeReg=nodestacksVersion, tmpdir=ctx.tmpdir)
        for node in ctx.nodeset:
            stack = node.nodestack
            args = (client1.name, stack.name, client1.keys_dir, stack.verhex, True)
            initRemoteKeys(*args)

        ctx.looper.add(client1)
        with pytest.raises(NotConnectedToAny):
            await client1.ensureConnectedToNodes()

    pool.run(go)


# noinspection PyIncorrectDocstring
def testSendRequestWithoutSignatureFails(pool):
    """
    A client request sent without a signature fails with an EmptySignature
    exception
    """

    async def go(ctx):
        client1, wallet = genTestClient(ctx.nodeset, tmpdir=ctx.tmpdir)

        # remove the client's ability to sign
        assert wallet.defaultId

        ctx.looper.add(client1)
        await client1.ensureConnectedToNodes()

        request = wallet.signOp(op=randomOperation())
        request.signature = None
        request = client1.submitReqs(request)[0][0]
        timeout = waits.expectedClientRequestPropagationTime(nodeCount)

        with pytest.raises(AssertionError):
            for node in ctx.nodeset:
                await eventually(
                    checkLastClientReqForNode, node, request,
                    retryWait=1, timeout=timeout)

        for n in ctx.nodeset:
            params = n.spylog.getLastParams(Node.handleInvalidClientMsg)
            ex = params['ex']
            msg, _ = params['wrappedMsg']
            assert isinstance(ex, MissingSignature)
            assert msg.get(f.IDENTIFIER.nm) == request.identifier

            params = n.spylog.getLastParams(Node.discard)
            reason = params["reason"]
            (msg, frm) = params["msg"]
            assert msg == request.as_dict
            assert msg.get(f.IDENTIFIER.nm) == request.identifier
            assert "MissingSignature" in reason

    pool.run(go)


CLI_REQ = pytest.mark.rbft_spec(section="IV", subsection="B", step=1)


@CLI_REQ("A client connects to all the nodes")
def testClientConnectsToAllNodes(client1):
    pass


@CLI_REQ("A client sends a request to all the nodes")
def testRequestFullRoundTrip(replied1, client1):
    pass


# noinspection PyIncorrectDocstring
def testEveryNodeRepliesWithNoFaultyNodes(looper, client1, replied1):
    """
    Every node will send a reply to the client when there are no faulty nodes in
    the system
    """

    def chk():
        receivedReplies = getRepliesFromClientInbox(client1.inBox,
                                                    replied1.reqId)
        print(receivedReplies)
        assert len(receivedReplies) == nodeCount

    looper.run(eventually(chk))


# noinspection PyIncorrectDocstring
def testReplyWhenRepliesFromAllNodesAreSame(looper, client1, wallet1):
    """
    When there are not faulty nodes, the client must get a reply from all the
    nodes.
    """
    request = sendRandomRequest(wallet1, client1)
    responseTimeout = waits.expectedTransactionExecutionTime(nodeCount)
    looper.run(
        eventually(checkResponseRecvdFromNodes, client1,
                   nodeCount, request.reqId,
                   retryWait=1, timeout=responseTimeout))
    checkResponseCorrectnessFromNodes(client1.inBox, request.reqId, F)


# noinspection PyIncorrectDocstring
def testReplyWhenRepliesFromExactlyFPlusOneNodesAreSame(looper,
                                                        client1,
                                                        wallet1):
    """
    When only :math:`f+1` replies from the nodes are matching, the client
    would accept the reply
    """
    request = sendRandomRequest(wallet1, client1)
    # exactly f + 1 => (3) nodes have correct responses
    # modify some (numOfResponses of type REPLY - (f + 1)) => 4 responses to
    # have a different operations
    responseTimeout = waits.expectedTransactionExecutionTime(nodeCount)
    looper.run(
        eventually(checkResponseRecvdFromNodes, client1,
                   nodeCount, request.reqId,
                   retryWait=1, timeout=responseTimeout))

    replies = (msg for msg, frm in client1.inBox
               if msg[OP_FIELD_NAME] == REPLY and
               msg[f.RESULT.nm][f.REQ_ID.nm] == request.reqId)

    # change two responses to something different
    for i in range(2):
        msg = next(replies)
        msg[f.RESULT.nm][f.SIG.nm] = str(i) + "Some random id"

    checkResponseCorrectnessFromNodes(client1.inBox, request.reqId, F)


# noinspection PyIncorrectDocstring
def testReplyWhenRequestAlreadyExecuted(looper, txnPoolNodeSet, client1, sent1):
    """
    When a request has already been executed the previously executed reply
    will be sent again to the client. An acknowledgement will not be sent
    for a repeated request.
    """
    waitForSufficientRepliesForRequests(looper, client1, requests=[sent1])

    originalRequestResponsesLen = nodeCount * 2
    duplicateRequestRepliesLen = nodeCount  # for a duplicate request we need to

    message_parts, err_msg = \
        client1.nodestack.prepare_for_sending(sent1, None)

    for part in message_parts:
        client1.nodestack._enqueueIntoAllRemotes(part, None)

    def chk():
        assertLength([response for response in client1.inBox
                      if (response[0].get(f.RESULT.nm) and
                          response[0][f.RESULT.nm][f.REQ_ID.nm] == sent1.reqId) or
                      (response[0].get(OP_FIELD_NAME) == REQACK and
                       response[0].get(f.REQ_ID.nm) == sent1.reqId)],
                     originalRequestResponsesLen + duplicateRequestRepliesLen)

    responseTimeout = waits.expectedTransactionExecutionTime(nodeCount)
    looper.run(eventually(chk, retryWait=1, timeout=responseTimeout))
