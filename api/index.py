from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime

app = FastAPI()

# Allow all origins (you can restrict this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rank-riser.vercel.app/"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/leetcode-contests/{username}")
async def get_leetcode_contests(username: str):
    graphql_url = "https://leetcode.com/graphql"

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",  # sometimes helps bypass restrictions
    }

    payload = {
        "operationName": "userContestRankingInfo",
        "query": """
            query userContestRankingInfo($username: String!) {
                userContestRankingHistory(username: $username) {
                    attended
                    rating
                    contest {
                        title
                        titleSlug
                        startTime
                    }
                    problemsSolved
                }
            }
        """,
        "variables": {
            "username": username
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(graphql_url, json=payload, headers=headers)

    data = response.json()["data"]["userContestRankingHistory"]
    attended_contests = [c for c in data if c["attended"]]

    results = []
    for contest in attended_contests:
        contest_info = contest["contest"]
        start_time = datetime.fromtimestamp(contest_info["startTime"]).strftime('%Y-%m-%d')
        results.append({
            "title": contest_info["title"],
            "url": f"https://leetcode.com/contest/{contest_info['titleSlug']}",
            "rating": contest["rating"],
            "problemsSolved": contest["problemsSolved"],
            "date": start_time,
        })

    return results
