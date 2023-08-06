class Watermark(dict):
    '''
    {
       "InputKey":"name of the .png or .jpg file",
       "Encryption":{
          "Mode":"S3|S3-AWS-KMS|AES-CBC-PKCS7|
             AES-CTR|AES-GCM",
          "Key":"encrypted and base64-encoded encryption key",
          "KeyMd5":"base64-encoded key digest",
          "InitializationVector":"base64-encoded initialization
             vector"
       },
       "PresetWatermarkId":"value of Video:Watermarks:Id in preset"
    }
    '''
