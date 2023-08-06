# Vodacom-NimbleHelper
A helper pip library for Vodacom Nimble

includes functionality to check parameters:
```
fields = [("name_like", "name"), ("id", "id")]
```
> Maps the first value in the tuple to value from the request specified
in the second value of the tuple e.g. front end passes through 'name' and the function maps that to 'name_like'
```
required_fields = [('name_like', 'id',)]
```
> This means that either 'name_like' or 'id' is required
```
required_fields = [('name_like',), ('id',)]
```
> This means that both 'name_like' and 'id' are required in the response

# Current Functionality
---------------------------------------------------------------------------------------------------------------------
## NimbleHelper class
> By Default the Nimble Helper class will check for the header 'HTTP_X_CONSUMER_ID' for authentication
### Check Get Parameters From Request
```
check_get_parameters(request, fields, required_fields, pk)
```
**request**
> The request made to the web service (this is the data that NimbleHelper Searches through)
**fields**
> The fields that NimbleHelper should look for in the request
**required_fields**
> Conditions of the fields that need to be passed through (see 'includes functionality to check parameters' above)
**pk**
>If a retrieve request is made, pass through the pk and the following format in fields
```
fields = [("name", "pk")]
```
> This will map pk to the value 'name'

### Check POST Parameters From Request
```
check_post_parameters(request, fields, required_fields, pk)
```
**request**
> The request made to the web service (this is the data that NimbleHelper Searches through)
**fields**
> The fields that NimbleHelper should look for in the request
**required_fields**
> Conditions of the fields that need to be passed through (see 'includes functionality to check parameters' above)

### Run Siebel Requests
```
_run_siebel_request(x_consumer_id, data)
```
> Runs a request through nimble gateway

**x_consumer_id**
> x_consumer_id of the user

**data**
> The data you wish to send to the gateway

### Check Authorization
```
_check_authorization(request)
```
**request**
> Pass through the request and the function will check it for the authorization header

## NimbleCodes
> This class allows for returning the correct response based on the input
```
http_code_helper(code, message, data)
```
**code**
> code of the response

**message**
> The message to return to the front end

**data**
> The data to pass through to the front end