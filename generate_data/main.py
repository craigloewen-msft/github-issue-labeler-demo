import requests
import json

# Replace with your GitHub token (obtain one at https://github.com/settings/tokens)
# Make sure the token has read access for issues
GITHUB_TOKEN = ''

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Content-Type': 'application/json',
    'User-Agent': 'IssueFetcher'
}

owner = 'microsoft'
repo = 'powertoys'

url = f'https://api.github.com/repos/{owner}/{repo}/issues'

page = 1
total_issues = 0
total_issue_count = 3000
issues = []

while total_issues < total_issue_count:
    try:
        params = {
            'page': page,
            'sort': 'created',
            'direction': 'desc'
        }

        response = requests.get(url, headers=headers, params=params)
        if not response.ok:
            print(f'Error: {response.status_code}')
            print(response.text)
            break

        issues_response = json.loads(response.text)

        if len(issues_response) == 0:
            break

        for issue in issues_response:
            # Get issue details
            title = issue['title']
            body = issue['body']
            number = issue['number']

            # Get labels (tags) for the issue
            issue_number = issue['number']

            labels = [label['name'] for label in issue['labels']]
            label_list = ','.join(labels) if labels else ''

            # If label_list contains 'Needs-Triage' then continue, or if it's a PR skip it
            if 'Needs-Triage' in labels:
                print("Skipping issue with label 'Needs-Triage'")
                continue

            if 'pull_request' in issue:
                print("Skipping a pull request")
                continue

            # Add to the issues list
            issues.append({
                'number': number,
                'title': title,
                'body': body,
                'label_list': label_list
            })

            print(f"Added issue #{number}")
            total_issues += 1

        print(f"Loading a new page, collected {total_issues} issues out of {total_issue_count}")
        page += 1

    except Exception as e:
        print(f'An error occurred: {str(e)}')
        break

# Save to JSON file
with open('github_issues.json', 'w') as f:
    json.dump(issues, f, indent=2)

print(f'Successfully saved {len(issues)} issues to github_issues.json')