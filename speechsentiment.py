from havenondemand.hodclient import *
from havenondemand.hodresponseparser import *
import sys

client = HODClient("YOUR_API_KEY")
parser = HODResponseParser()

def asyncRequestCompleted(response):
    jobID = parser.parse_jobid(response)
    if jobID is None:
        errorObj = parser.get_last_error()
        for err in errorObj.errors:
            print ("Error code: %d \nReason: %s \nDetails: %s\n" % (err.error,err.reason, err.detail))
    else:
        client.get_job_status(jobID, requestCompleted)

def requestCompleted(response):
    payloadObj = parser.parse_payload(response)
    if payloadObj is None:
        errorObj = parser.get_last_error()
        for err in errorObj.errors:
            if err.error == ErrorCode.QUEUED:
                time.sleep(2)
                client.get_job_status(err.jobID, requestCompleted)
                return
            elif err.error == ErrorCode.IN_PROGRESS:
                time.sleep(10)
                client.get_job_status(err.jobID, requestCompleted)
                return
            else:
                print(err.reason)
    else:
        resp = ""
        results = payloadObj["results"]
        for result in results:
            if result['name'] == "recognized_text":
                resp += result['name'] + "\n"
                resp += result['value'] + "\n"
            elif result['name'] == "sentiment_result":
                resp += result['name'] + "\n"
                positives = result['value']["positive"]
                resp += "Positive:\n"
                for pos in positives:
                    if pos.get('sentiment'):
                        resp += "Sentiment: " + pos["sentiment"] + "\n"
                    if pos.get('topic'):
                        resp += "Topic: " + pos["topic"] + "\n"
                    resp += "Score: " + "%f " % (pos["score"]) + "\n"
                negatives = result['value']["negative"]
                resp += "Negative:\n"
                for neg in negatives:
                    if neg.get('sentiment'):
                        resp += "Sentiment: " + neg["sentiment"] + "\n"
                    if neg.get('topic'):
                        resp += "Topic: " + neg["topic"] + "\n"
                    resp += "Score: " + "%f " % (neg["score"]) + "\n"
                aggregate = result['value']["aggregate"]
                resp += "Aggregate:\n"
                resp += "Sentiment: " + aggregate["sentiment"] + "\n"
                resp += "Score: " + "%f " % (aggregate["score"])
        print(resp)

hodApp = "speechsentimentanalysis"
params = {}
params['file'] = [('mediaFile','testdata/attendant.mp3')]
response = client.post_request_combination(params, hodApp, True, asyncRequestCompleted)