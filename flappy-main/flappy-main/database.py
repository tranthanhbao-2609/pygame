from pymongo import MongoClient
import datetime

# ==============================
# CONNECT TO MONGODB
# ==============================
client = MongoClient("mongodb+srv://2331540308_db_user:khang311005@cluster0.8w2jm8f.mongodb.net/?appName=Cluster0")
db = client["flappy_bird"]

players = db["players"]          # Lưu 1 record/người chơi
leaderboard = db["leaderboard"]  # Lưu top N người chơi

TOP_N = 10  # số người chơi lưu trong leaderboard

# ==============================
# Tạo hoặc load người chơi
# ==============================
def load_or_create_player(name):
    """
    Tải thông tin player. Nếu chưa có, tạo mới.
    """
    player = players.find_one({"name": name})
    if player:
        return player
    else:
        new_player = {
            "name": name,
            "score": 0,
            "ai_score": 0,
            "best_score": 0,
            "createdAt": datetime.datetime.now()
        }
        players.insert_one(new_player)
        return new_player

# ==============================
# Cập nhật score người chơi
# ==============================
def update_player_score(name, score, ai_score=0):
    """
    Cập nhật điểm người chơi:
    - Nếu score mới cao hơn best_score, update.
    - Cập nhật leaderboard top N.
    """
    player = players.find_one({"name": name})

    if player is None:
        # Nếu chưa tồn tại (trường hợp hiếm)
        player_data = {
            "name": name,
            "score": score,
            "ai_score": ai_score,
            "best_score": score,
            "createdAt": datetime.datetime.now()
        }
        players.insert_one(player_data)
        new_best = score
    else:
        # Cập nhật score, AI score
        new_best = max(player.get("best_score", 0), score)
        players.update_one(
            {"name": name},
            {"$set": {
                "score": score,
                "ai_score": ai_score,
                "best_score": new_best,
                "updatedAt": datetime.datetime.now()
            }}
        )

    # Cập nhật leaderboard
    update_leaderboard(name, new_best, ai_score)

    return new_best

# ==============================
# Lấy điểm cao nhất (top 1)
# ==============================
def get_highest_score():
    """
    Trả về score cao nhất trong leaderboard
    """
    top = leaderboard.find_one(sort=[("score", -1)])
    return top["score"] if top else 0

# ==============================
# Lấy leaderboard top N
# ==============================
def get_leaderboard():
    """
    Lấy danh sách top N người chơi theo score giảm dần
    """
    return list(leaderboard.find().sort("score", -1).limit(TOP_N))

# ==============================
# Cập nhật leaderboard top N
# ==============================
def update_leaderboard(name, score, ai_score):
    """
    Cập nhật top N leaderboard
    """
    # Thêm hoặc update record người chơi trong leaderboard
    leaderboard.update_one(
        {"name": name},
        {"$set": {
            "score": score,
            "ai_score": ai_score,
            "updatedAt": datetime.datetime.now()
        }},
        upsert=True
    )

    # Giữ lại top N, xóa những người không nằm trong top N
    top_players = list(leaderboard.find().sort("score", -1).limit(TOP_N))
    top_names_scores = [(p["name"], p["score"]) for p in top_players]

    for p in leaderboard.find():
        if (p["name"], p["score"]) not in top_names_scores:
            leaderboard.delete_one({"_id": p["_id"]})

# ==============================
# TEST NHANH
# ==============================
if __name__ == "__main__":
    print("=== Player 1 chơi ===")
    best1 = update_player_score("Hung", 10)
    print("Hung best score:", best1)

    print("\n=== Player 2 chơi ===")
    best2 = update_player_score("Lan", 12)
    print("Lan best score:", best2)

    print("\n=== Player 1 chơi lại ===")
    best1_again = update_player_score("Hung", 15)
    print("Hung best score:", best1_again)

    print("\n=== Leaderboard hiện tại ===")
    for p in get_leaderboard():
        print(p)

    print("\n=== Điểm cao nhất hiện tại ===")
    print(get_highest_score())
