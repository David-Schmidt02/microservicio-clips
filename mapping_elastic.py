{
  "streaming_tv" : {
    "mappings" : {
      "properties" : {
        "@timestamp" : {
          "type" : "date"
        },
        "channel" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "channel_id" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "channel_status" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "channel_url" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "datetime" : {
          "type" : "date"
        },
        "filtered" : {
          "type" : "boolean"
        },
        "processed_at" : {
          "type" : "date"
        },
        "source_id" : {
          "type" : "keyword"
        },
        "text" : {
          "type" : "text",
          "fields" : {
            "clean" : {
              "type" : "text",
              "analyzer" : "clean_text_analyzer",
              "fielddata" : true
            },
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          },
          "analyzer" : "spanish_analyzer",
          "fielddata" : true
        },
        "timestamp" : {
          "type" : "keyword"
        },
        "transcription_time" : {
          "type" : "date"
        }
      }
    }
  }
}

## Ejemplo de un registro

