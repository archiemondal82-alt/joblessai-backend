def normalize(data):
    data["profile_summary"] = data.get("profile_summary", "")
    data["current_skills"] = data.get("current_skills", [])
    data["careers"] = data.get("careers", [])

    for c in data["careers"]:

        # Safe match score
        try:
            c["match_score"] = int(c.get("match_score", 0))
        except:
            c["match_score"] = 0

        c["salary_range"] = c.get("salary_range", "")
        c["reason"] = c.get("reason", "")

        # 🔥 FIXED skill_gap_analysis (THIS WAS CRASHING)
        safe_gap = {}
        for k, v in c.get("skill_gap_analysis", {}).items():
            try:
                # Handle list like [0.6]
                if isinstance(v, list):
                    v = v[0] if len(v) > 0 else 0

                # Handle string like "0.6"
                safe_gap[k] = float(v)

            except:
                safe_gap[k] = 0.0

        c["skill_gap_analysis"] = safe_gap

        c["next_steps"] = c.get("next_steps", [])
        c["learning_path"] = c.get("learning_path", [])
        c["interview_tips"] = c.get("interview_tips", [])
        c["job_search_keywords"] = c.get("job_search_keywords", "")
        c["top_companies"] = c.get("top_companies", [])
        c["certifications"] = c.get("certifications", [])

    return data
