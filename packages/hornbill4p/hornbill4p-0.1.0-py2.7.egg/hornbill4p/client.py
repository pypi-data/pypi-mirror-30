# -*- coding=UTF-8 -*-

import json
import grpc
from hornbill4p import hornbill_pb2_grpc, hornbill_pb2


class HornbillRpcClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = hornbill_pb2_grpc.ClassifierStub(self.channel)

    def classify(self, content, workflows):
        """
        hornbill classification
        :param content: content to analysis, string
        :param workflows: list of string, hornbill classifier id
        :return: hornbill result ADTWT$1|SNTTWT$1
        """

        doc = {"id": "", "data": {"Text": content}, "documentType": "WEIBO"}
        doc = json.dumps(doc, ensure_ascii=True)
        doc_bytes = bytes(doc, "utf8")
        response = self.stub.Classify(hornbill_pb2.BytesRequest(document=doc_bytes, workflows=workflows))
        return json.loads(response.hornbillResult)

    def batch_classify(self, contents, workflows):

        docs = []
        for content in contents:
            doc = {"id": "", "data": {"Text": content}, "documentType": "WEIBO"}
            docs.append(doc)
        docs = json.dumps(docs, ensure_ascii=True)
        docs_bytes = bytes(docs, "utf8")
        response = self.stub.BatchClassify(hornbill_pb2.BytesRequest(document=docs_bytes, workflows=workflows))

        return json.loads(response.hornbillResult)
