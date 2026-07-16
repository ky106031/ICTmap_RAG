CONDITION_LABELS = [
    "Grade",
    "Field",
    "Unit",
    "ICT_Hardware",
    "ICT_Software",
    "ICT_Artifact",
    "ICT_Function",
    "Educational_Opportunity",
    "Educational_Effect",
]


PATH_PATTERNS = [
    {
        "path_type": "hardware-software-artifact-function-opportunity-effect",
        "cypher": """
        MATCH p =
            (paper:Paper)-[r0:CONTAINS]->(pr:Practice)
            -[r1:USES_HARDWARE]->(h:ICT_Hardware)
            -[r2:RUNS_SOFTWARE]->(s:ICT_Software)
            -[r3:CREATES]->(a:ICT_Artifact)
            -[r4:HAS_FUNCTION]->(func:ICT_Function)
            -[r5:ENABLES]->(opp:Educational_Opportunity)
            -[r6:PROMOTES]->(eff:Educational_Effect)
        WHERE ALL(r IN relationships(p) WHERE r.practice_id = pr.practice_id)
        """
    },
    {
        "path_type": "hardware-software-function-opportunity-effect",
        "cypher": """
        MATCH p =
            (paper:Paper)-[r0:CONTAINS]->(pr:Practice)
            -[r1:USES_HARDWARE]->(h:ICT_Hardware)
            -[r2:RUNS_SOFTWARE]->(s:ICT_Software)
            -[r3:HAS_FUNCTION]->(func:ICT_Function)
            -[r4:ENABLES]->(opp:Educational_Opportunity)
            -[r5:PROMOTES]->(eff:Educational_Effect)
        WHERE ALL(r IN relationships(p) WHERE r.practice_id = pr.practice_id)
        WITH p, paper, pr, h, s, null AS a, func, opp, eff
        """
    },
    {
        "path_type": "hardware-artifact-function-opportunity-effect",
        "cypher": """
        MATCH p =
            (paper:Paper)-[r0:CONTAINS]->(pr:Practice)
            -[r1:USES_HARDWARE]->(h:ICT_Hardware)
            -[r2:CREATES]->(a:ICT_Artifact)
            -[r3:HAS_FUNCTION]->(func:ICT_Function)
            -[r4:ENABLES]->(opp:Educational_Opportunity)
            -[r5:PROMOTES]->(eff:Educational_Effect)
        WHERE ALL(r IN relationships(p) WHERE r.practice_id = pr.practice_id)
        WITH p, paper, pr, h, null AS s, a, func, opp, eff
        """
    },
    {
        "path_type": "hardware-function-opportunity-effect",
        "cypher": """
        MATCH p =
            (paper:Paper)-[r0:CONTAINS]->(pr:Practice)
            -[r1:USES_HARDWARE]->(h:ICT_Hardware)
            -[r2:HAS_FUNCTION]->(func:ICT_Function)
            -[r3:ENABLES]->(opp:Educational_Opportunity)
            -[r4:PROMOTES]->(eff:Educational_Effect)
        WHERE ALL(r IN relationships(p) WHERE r.practice_id = pr.practice_id)
        WITH p, paper, pr, h, null AS s, null AS a, func, opp, eff
        """
    },
]