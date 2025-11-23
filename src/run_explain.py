
def  run_explain(collection,query,sort=None, typeOfQuery = "find"):
    #Build the query
    
    if typeOfQuery == "find":
        cursor = collection.find(query)
    elif typeOfQuery == "aggregate":
        cursor = collection.aggregate(query)
    else:
        raise ValueError(f"Unsupported query type: {typeOfQuery}")

    #Add sorting if provided
    if sort is not None:
        cursor = cursor.sort(sort)

    #lauch explain with execution statistics
    explain_data = cursor.explain()

    planner = explain_data.get("queryPlanner", {})
    winning_plan = planner.get("winningPlan", {})
    stats = explain_data.get("executionStats", {})

    def parse_stage(stage):
       #detailed dictionary of each stage
        result = stage.copy()
        if "inputStage" in stage:
            # Appel récursif pour traiter le stage interne
            result["inputStage"] = parse_stage(stage["inputStage"])
        # If several nested stages
        if "inputStages" in stage:
            result["inputStages"] = [parse_stage(s) for s in stage["inputStages"]]
        return result
    
    execution_stages = parse_stage(stats.get("executionStages", {}))

    # Secure extraction of certain metrics from the main stage
    index_name = None
    index_bounds = None
    def extract_index_info(stage):
        nonlocal index_name, index_bounds
        if stage.get("stage") == "IXSCAN":
            index_name = stage.get("indexName")
            index_bounds = stage.get("indexBounds")
        # Check the sub-internships
        if "inputStage" in stage:
            extract_index_info(stage["inputStage"])
        if "inputStages" in stage:
            for s in stage["inputStages"]:
                extract_index_info(s)

    extract_index_info(execution_stages)  
# Final report with all the important metrics
    return {
        "namespace": planner.get("namespace"),
        "parsedQuery": planner.get("parsedQuery"),
        "optimizationTimeMillis": planner.get("optimizationTimeMillis"),
        "rejectedPlans": planner.get("rejectedPlans", []),
        "executionSuccess": stats.get("executionSuccess"),
        "nReturned": stats.get("nReturned"),
        "executionTimeMillis": stats.get("executionTimeMillis"),
        "totalDocsExamined": stats.get("totalDocsExamined"),
        "totalKeysExamined": stats.get("totalKeysExamined"),
        "executionStages": execution_stages,
        "indexName": index_name,
        "indexBounds": index_bounds,
        "memoryUsageBytesEstimate": stats.get("executionStages", {}).get("maxMemoryUsageBytes"),
        "sortPattern": explain_data.get("sortPattern")
    }