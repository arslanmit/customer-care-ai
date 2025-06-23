import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from zoneinfo import ZoneInfo

def load_conversations(path: str):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        conversations = list(data.get('_default', {}).values())
        print(f"Successfully loaded {len(conversations)} conversations")
        if conversations:
            print(f"First conversation ID: {conversations[0].get('sender_id', 'Unknown')}")
        return conversations
    except Exception as e:
        print(f"Error loading conversations: {str(e)}")
        return []

def compute_summary(convs):
    rows = []
    for conv in convs:
        sid = conv['sender_id']
        events = conv.get('events', [])
        total_events = len(events)
        fallback_count = sum(
            1 for e in events
            if (e.get('event') == 'action' and e.get('name') == 'action_default_fallback') or
               (e.get('event') == 'user' and e.get('parse_data', {}).get('intent', {}).get('name') == 'nlu_fallback')
        )
        rows.append({
            'sender_id': sid,
            'total_events': total_events,
            'fallbacks': fallback_count
        })
    return pd.DataFrame(rows)

def compute_intents(convs):
    intents = [
        e['parse_data']['intent']['name']
        for conv in convs
        for e in conv.get('events', [])
        if e.get('event') == 'user' and 'parse_data' in e
    ]
    return pd.Series(intents).value_counts().head(10) \
             .reset_index().rename(columns={'index': 'intent', 0: 'count'})

def compute_response_times(convs):
    rows = []
    all_rts = []
    for conv in convs:
        sid = conv['sender_id']
        events = conv.get('events', [])
        rts = []
        for i, e in enumerate(events):
            if e.get('event') == 'user':
                t_user = e.get('timestamp')
                for ne in events[i+1:]:
                    if ne.get('event') == 'bot':
                        rt = ne.get('timestamp') - t_user
                        rts.append(rt)
                        all_rts.append(rt)
                        break
        rows.append({
            'sender_id': sid,
            'avg_rt_s': sum(rts)/len(rts) if rts else None,
            'min_rt_s': min(rts) if rts else None,
            'max_rt_s': max(rts) if rts else None
        })
    return pd.DataFrame(rows), all_rts

def make_dashboard(conversations, df_summary, df_intents, df_rt, all_rts):
    import os
    
    # Create dashboard directory if it doesn't exist
    output_dir = '../dashboard'
    os.makedirs(output_dir, exist_ok=True)
    
    now = datetime.now(ZoneInfo('Europe/Berlin')).strftime('%Y-%m-%d_%H-%M-%S')
    output_file = os.path.join(output_dir, f'rasa_dashboard_{now}.png')
    
    # Set a non-interactive backend to avoid display issues
    import matplotlib
    matplotlib.use('Agg')  # Use a non-interactive backend
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    fig.suptitle(f'Rasa Conversation Dashboard — {datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M:%S %Z")}', 
                 fontsize=20, y=0.98)

    # 1. Summary table
    axes[0, 0].axis('off')
    axes[0, 0].table(
        cellText=df_summary.values,
        colLabels=df_summary.columns,
        loc='center'
    )
    axes[0, 0].set_title('Conversation Summary', pad=20)

    # 2. Histogram of total events
    axes[0, 1].hist(df_summary['total_events'], bins=10)
    axes[0, 1].set_title('Total Events per Conversation')
    axes[0, 1].set_xlabel('Total Events')
    axes[0, 1].set_ylabel('Conversations')

    # 3. Histogram of fallbacks
    axes[1, 0].hist(df_summary['fallbacks'], bins=int(df_summary['fallbacks'].max())+1)
    axes[1, 0].set_title('Fallback Counts per Conversation')
    axes[1, 0].set_xlabel('Fallback Count')
    axes[1, 0].set_ylabel('Conversations')

    # 4. Bar chart of top intents
    axes[1, 1].bar(df_intents['intent'], df_intents['count'])
    axes[1, 1].set_title('Top 10 User Intents')
    axes[1, 1].set_xlabel('Intent')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].tick_params(axis='x', rotation=45)

    # 5. Histogram of average response times
    axes[2, 0].hist(df_rt['avg_rt_s'].dropna(), bins=10)
    axes[2, 0].set_title('Avg Response Time per Conversation (s)')
    axes[2, 0].set_xlabel('Avg Response Time (s)')
    axes[2, 0].set_ylabel('Conversations')

    # 6. Histogram of individual response times
    axes[2, 1].hist(all_rts, bins=20)
    axes[2, 1].set_title('Individual Response Times (s)')
    axes[2, 1].set_xlabel('Response Time (s)')
    axes[2, 1].set_ylabel('Turns')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Dashboard saved to: {os.path.abspath(output_file)}")

def main():
    path = 'data/rasa_conversations.json'
    print(f"Loading conversations from: {path}")
    convs = load_conversations(path)
    
    if not convs:
        print("No conversations loaded. Exiting.")
        return
    df_summary = compute_summary(convs)
    df_intents = compute_intents(convs)
    df_rt, all_rts = compute_response_times(convs)
    make_dashboard(convs, df_summary, df_intents, df_rt, all_rts)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()