import json

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def mark_all_as_voted():
    members = load_json('group_members.json')
    voters = load_json('elimination_voters.json')
    for member in members:
        voters[str(member['id'])] = True
    save_json('elimination_voters.json', voters)
    print(f"Marked {len(members)} users as voted in elimination_voters.json!")

def add_specific_users():
    voters = load_json('elimination_voters.json')
    user_ids = input('Enter user IDs who already voted (comma-separated): ').split(',')
    user_ids = [uid.strip() for uid in user_ids if uid.strip()]
    for uid in user_ids:
        voters[uid] = True
    save_json('elimination_voters.json', voters)
    print(f"Added {len(user_ids)} users as voted in elimination_voters.json!")

def main():
    print("Choose an option:")
    print("1. Mark ALL group members as voted (automated)")
    print("2. Add specific user IDs as voted (manual)")
    choice = input("Enter 1 or 2: ").strip()
    if choice == '1':
        mark_all_as_voted()
    elif choice == '2':
        add_specific_users()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
