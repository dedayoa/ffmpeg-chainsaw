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
        "statusURL": {
            "type": "string",
            "description": "The webhook url where status updates are sent"
        },
        "destination": {
            "type": "object",
            "description": "The location where the converted file should be sent. Options are s3, sftp, http.",
            "properties": {
                "protocol": {
                    "type": "string",
                    "enum": ["s3", "http", "ftp"]
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
                                "regionName": {
                                    "type": "string"
                                },
                                "bucketName": {
                                    "type": "string"
                                }
                            }
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
                            }
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
                                }
                            },
                            "required": ['url']
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