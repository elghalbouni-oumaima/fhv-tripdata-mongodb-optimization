{
    "explainVersion": "1",
    "queryPlanner": {
        "namespace": "trips_db.fhvhv_trips_2021-10",
        "parsedQuery": {
            "dropoff_datetime": {
                "$eq": 1633065952
            }
        },
        "indexFilterSet": false,
        "optimizationTimeMillis": 0,
        "maxIndexedOrSolutionsReached": false,
        "maxIndexedAndSolutionsReached": false,
        "maxScansToExplodeReached": false,
        "prunedSimilarIndexes": false,
        "winningPlan": {
            "isCached": false,
            "stage": "EOF",
            "type": "nonExistentNamespace"
        },
        "rejectedPlans": []
    },
    "executionStats": {
        "executionSuccess": true,
        "nReturned": 0,
        "executionTimeMillis": 0,
        "totalKeysExamined": 0,
        "totalDocsExamined": 0,
        "executionStages": {
            "isCached": false,
            "stage": "EOF",
            "nReturned": 0,
            "executionTimeMillisEstimate": 0,
            "works": 1,
            "advanced": 0,
            "needTime": 0,
            "needYield": 0,
            "saveState": 0,
            "restoreState": 0,
            "isEOF": 1,
            "type": "nonExistentNamespace"
        },
        "allPlansExecution": []
    },
    "queryShapeHash": "68F31E123EDEF1C80353279995B67E488624FD57853182C30F62F9F1745495E1",
    "command": {
        "find": "fhvhv_trips_2021-10",
        "filter": {
            "dropoff_datetime": 1633065952
        },
        "$db": "trips_db"
    },
    "serverInfo": {
        "host": "DESKTOP-NRD95P9",
        "port": 27017,
        "version": "8.2.1",
        "gitVersion": "3312bdcf28aa65f5930005e21c2cb130f648b8c3"
    },
    "serverParameters": {
        "internalQueryFacetBufferSizeBytes": 104857600,
        "internalQueryFacetMaxOutputDocSizeBytes": 104857600,
        "internalLookupStageIntermediateDocumentMaxSizeBytes": 104857600,
        "internalDocumentSourceGroupMaxMemoryBytes": 104857600,
        "internalQueryMaxBlockingSortMemoryUsageBytes": 104857600,
        "internalQueryProhibitBlockingMergeOnMongoS": 0,
        "internalQueryMaxAddToSetBytes": 104857600,
        "internalDocumentSourceSetWindowFieldsMaxMemoryBytes": 104857600,
        "internalQueryFrameworkControl": "trySbeRestricted",
        "internalQueryPlannerIgnoreIndexWithCollationForRegex": 1
    },
    "ok": 1.0
}