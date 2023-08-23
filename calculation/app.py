import boto3
import utils
import json


def save_trace_to_s3():
    trace = utils.generate_trace()
    json_data = json.dumps(trace, cls=utils.NumpyEncoder)
    s3 = boto3.resource('s3')
    
    s3object = s3.Object('bayesian-soccer-traces-matthew-burke', 'latest_trace.json')
    
    s3object.put(
        Body=(bytes(json.dumps(json_data).encode('UTF-8')))
    )
    return {"response":"trace_updated"}

if __name__ == "__main__":
    save_trace_to_s3()
