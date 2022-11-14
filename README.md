# Smart Album Backend
A smart photo album which web application that can be searched using natural language through both text and voice. Uploaded photos are automatically tagged using Computer Vision and user provided labels. These labels are then used for searching the smart album for results and display them back to the user.

## Objective
1. Launch an OpenSearch instance. Using AWS OpenSearch service, create a new domain called “photos”.
2. Create a S3 bucket (B2) to store the photos. Create a Lambda function (LF1) called “index-photos”. Set up a PUT event trigger4 on the photos S3 bucket (B2), such that whenever a photo gets uploaded to the bucket, it triggers the Lambda function (LF1) to index it.
3. Implement the indexing Lambda function (LF1). Given a S3 PUT event (E1) detect labels in the image, using Rekognition (“detectLabels” method).
Use the S3 SDK’s headObject method to retrieve the S3 metadata created at the object’s upload time. Retrieve the x-amz-meta-customLabels metadata field, if applicable, and create a JSON array (A1) with the labels. Store a JSON object in an OpenSearch index (“photos”) that references the S3 object from the PUT event (E1) and append string labels to the labels array (A1), one for each label detected by Rekognition.
Use the following schema for the JSON object:
```
{
    “objectKey”: “my-photo.jpg”,
    “bucket”: “my-photo-bucket”,
    “createdTimestamp”: “2018-11-05T12:40:02”,
    “labels”: [
        “person”,
        “dog”,
        “ball”,
        “park”
    ]
}
```
4. Create a Lambda function (LF2) called “search-photos”. Create an Amazon Lex bot to handle search queries. Create a Lambda function (LF2) called “search-photos”. Create an Amazon Lex bot to handle search queries.
5. Build an API using API Gateway. The Swagger API documentation for the API can be found here: [Link](https://github.com/001000001/ai-photo-search-columbia-f2018/blob/master/swagger.yaml). The API should have two methods PUT /photos. Set up the method as an Amazon S3 Proxy8. This will allow API Gateway to forward your PUT request directly to S3. Use a custom x-amz-meta-customLabels HTTP header to include any custom labels the user specifies at upload time. GET /search?q={query text} Connect this method to the search Lambda function (LF2). Setup an API key for your two API methods. Deploy the API. Generate a SDK for the API (SDK1)
6. Define a pipeline (P1) in AWS CodePipeline that builds and deploys the code for/to all your Lambda functions. Define a pipeline (P2) in AWS CodePipeline that builds and deploys your frontend code to its corresponding S3 bucket.
7. Create a CloudFormation template (T1) to represent all the infrastructure resources (ex. Lambdas, OpenSearch, API Gateway, CodePipeline, etc.) and permissions (IAM policies, roles, etc.).

## Architecture
![Architecture](/assets/design.png)
