instruction_schema = {
    "type": "object",
    "properties": {
        "ffmpegArgs": {
            "type": "array",
            "description": "The ffmpeg command line arguments",
            "items": {
                "type": "string"
            }
        },
        "outputFileMimeType": {
            "type": "string",
            "description": "The ouput file mime type"
        },
        "outputFileExt": {
            "type": "string",
            "description": "The ouput file extension"
        },        
        "outputFileName": {
            "type": "string",
            "description": "The name of the output file name including the extension. A random name is provided if not provided"
        },
        "updateCallback": {
            "type": "object",
            "description": "The callback to the webhook where updates are sent",
            "properties": {
                "url": {
                    "type": "string"
                },
                "username": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                },
                "customHeaders": {
                    "type": "object",
                    "description": "Custom headers that should be sent along with http request"
                }
            },
            "required": ["url"]
        },
        "destination": {
            "type": "object",
            "description": "The location where the converted file should be sent. Options are s3, sftp, http.",
            "properties": {
                "protocol": {
                    "type": "string",
                    "enum": ["s3", "http", "sftp", "disk"]
                }
            },
            "allOf": [
                {
                    "if": {
                        "properties": { "protocol": {"const": "s3"} }
                    },
                    "then": {
                        "properties": { "configuration": {
                            "type": "object",
                            "properties": {
                                "awsAccessKeyId": {
                                    "type": "string"
                                },
                                "awsSecretAccessKey": {
                                    "type": "string"
                                },
                                "bucketName": {
                                    "type": "string"
                                },
                                "extraArgs": {
                                    "type": "object"
                                }
                            },
                            "required": ["awsAccessKeyId", "awsSecretAccessKey", "bucketName"]
                        }}
                    }
                },
                {
                    "if": {
                        "properties": { "protocol": {"const": "sftp"} }
                    },
                    "then": {
                        "properties": { "configuration": {
                            "type": "object",
                            "properties": {
                                "host": {
                                    "type": "string"
                                },
                                "port": {
                                    "type": "number"
                                },
                                "directory": {
                                    "type": "string"
                                },
                                "username": {
                                    "type": "string"
                                },
                                "password": {
                                    "type": "string"
                                }
                            },
                            "required": ["host","username","password"]
                        }}
                    }
                },
                {
                    "if": {
                        "properties": { "protocol": {"const": "http"} }
                    },
                    "then": {
                        "properties": { "configuration": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "The http/s url to upload the output file to"
                                },
                                "username": {
                                    "type": "string"
                                },
                                "password": {
                                    "type": "string"
                                },
                                "fieldName": {
                                    "type": "string",
                                    "description": "The expected field name of the file to be uploaded for the http post request. Defaults to 'file'"
                                },
                                "customHeaders": {
                                    "type": "object",
                                    "description": "Custom headers that should be sent along with http request"
                                }
                            },
                            "required": ['url']
                        }}
                    }
                },
                {
                    "if": {
                        "properties": { "protocol": {"const": "disk"} }
                    },
                    "then": {
                        "properties": { "configuration": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "The directory into which the file should be stored"
                                }
                            },
                            "required": ['directory']
                        }}
                    }
                }
            ],
            "required": ["protocol"]
        }
    },
    "required": ["ffmpegArgs", "outputFileExt", "destination"],
    "additionalProperties": False
}