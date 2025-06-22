"""
Analyze Rasa conversation data from data/rasa_conversations.json
"""
import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Constants
CONVERSATIONS_FILE = "data/rasa_conversations.json"
REPORT_FILE = "conversation_analysis_report.md"
PLOTS_DIR = "analysis_plots"


def load_conversations() -> Dict[str, Any]:
    """Load conversations from the JSON file."""
    try:
        with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {CONVERSATIONS_FILE} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not parse {CONVERSATIONS_FILE}. File may be corrupted.")
        return {}


def analyze_conversations(conversations: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze conversation data and return statistics."""
    if not conversations or "_default" not in conversations:
        return {}
    
    stats = {
        "total_conversations": 0,
        "total_messages": 0,
        "intent_distribution": Counter(),
        "conversation_lengths": [],
        "slots_usage": defaultdict(int),
        "entities_usage": defaultdict(int),
        "timestamp_analysis": {
            "by_hour": defaultdict(int),
            "by_weekday": defaultdict(int)
        },
        "fallback_analysis": {
            "total_fallbacks": 0,
            "conversations_with_fallbacks": 0
        }
    }
    
    for conv_id, conversation in conversations["_default"].items():
        if not isinstance(conversation, dict):
            continue
            
        stats["total_conversations"] += 1
        
        # Analyze slots
        slots = conversation.get("slots", {})
        for slot_name, slot_value in slots.items():
            if slot_value:  # Only count non-None slots
                stats["slots_usage"][slot_name] += 1
        
        # Count fallbacks
        num_fallbacks = slots.get("num_fallbacks", 0)
        if num_fallbacks > 0:
            stats["fallback_analysis"]["total_fallbacks"] += num_fallbacks
            stats["fallback_analysis"]["conversations_with_fallbacks"] += 1
        
        # Analyze events
        events = conversation.get("events", [])
        stats["total_messages"] += len(events)
        stats["conversation_lengths"].append(len(events))
        
        for event in events:
            # Analyze intents
            if event.get("event") == "user":
                intent = event.get("parse_data", {}).get("intent", {}).get("name")
                if intent:
                    stats["intent_distribution"][intent] += 1
                
                # Analyze entities
                entities = event.get("parse_data", {}).get("entities", [])
                for entity in entities:
                    entity_type = entity.get("entity")
                    if entity_type:
                        stats["entities_usage"][entity_type] += 1
            
            # Analyze timestamps
            if "timestamp" in event:
                try:
                    dt = datetime.fromisoformat(event["timestamp"])
                    stats["timestamp_analysis"]["by_hour"][dt.hour] += 1
                    stats["timestamp_analysis"]["by_weekday"][dt.weekday()] += 1
                except (ValueError, TypeError):
                    pass
    
    # Calculate averages
    if stats["total_conversations"] > 0:
        stats["avg_messages_per_conversation"] = (
            stats["total_messages"] / stats["total_conversations"]
        )
    else:
        stats["avg_messages_per_conversation"] = 0
    
    return stats


def create_visualizations(stats: Dict[str, Any]) -> None:
    """Create visualizations from the conversation statistics."""
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)
    
    # Plot intent distribution
    if stats["intent_distribution"]:
        plt.figure(figsize=(12, 6))
        intents = list(stats["intent_distribution"].keys())
        counts = list(stats["intent_distribution"].values())
        
        plt.bar(intents, counts)
        plt.title("Intent Distribution")
        plt.xlabel("Intent")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "intent_distribution.png"))
        plt.close()
    
    # Plot conversation lengths
    if stats["conversation_lengths"]:
        plt.figure(figsize=(10, 5))
        plt.hist(stats["conversation_lengths"], bins=20, alpha=0.7, color='skyblue')
        plt.title("Conversation Length Distribution")
        plt.xlabel("Number of Messages")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "conversation_lengths.png"))
        plt.close()
    
    # Plot entities usage
    if stats["entities_usage"]:
        plt.figure(figsize=(12, 6))
        entities = list(stats["entities_usage"].keys())
        counts = list(stats["entities_usage"].values())
        
        plt.bar(entities, counts)
        plt.title("Entity Type Usage")
        plt.xlabel("Entity Type")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "entity_usage.png"))
        plt.close()
    
    # Plot messages by hour
    if stats["timestamp_analysis"]["by_hour"]:
        hours = sorted(stats["timestamp_analysis"]["by_hour"].items())
        x, y = zip(*hours)
        
        plt.figure(figsize=(10, 5))
        plt.plot(x, y, marker='o')
        plt.title("Messages by Hour of Day")
        plt.xlabel("Hour of Day (0-23)")
        plt.ylabel("Number of Messages")
        plt.xticks(range(0, 24))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "messages_by_hour.png"))
        plt.close()


def generate_report(stats: Dict[str, Any]) -> str:
    """Generate a markdown report from the conversation statistics."""
    report = ["# Rasa Conversation Analysis Report\n"]
    
    # Basic stats
    report.append("## 📊 Basic Statistics\n")
    report.append(f"- **Total Conversations:** {stats.get('total_conversations', 0)}")
    report.append(f"- **Total Messages:** {stats.get('total_messages', 0)}")
    report.append(
        f"- **Average Messages per Conversation:** {stats.get('avg_messages_per_conversation', 0):.2f}"
    )
    
    # Fallback analysis
    fallbacks = stats.get("fallback_analysis", {})
    report.append("\n## ⚠️ Fallback Analysis\n")
    report.append(f"- **Total Fallbacks:** {fallbacks.get('total_fallbacks', 0)}")
    report.append(
        f"- **Conversations with Fallbacks:** {fallbacks.get('conversations_with_fallbacks', 0)}"
    )
    
    # Intent distribution
    if stats.get("intent_distribution"):
        report.append("\n## 🎯 Intent Distribution\n")
        report.append("| Intent | Count | Percentage |")
        report.append("|--------|-------|------------|")
        
        total_intents = sum(stats["intent_distribution"].values())
        for intent, count in stats["intent_distribution"].most_common():
            percentage = (count / total_intents) * 100
            report.append(f"| `{intent}` | {count} | {percentage:.1f}% |")
    
    # Entities usage
    if stats.get("entities_usage"):
        report.append("\n## 🔍 Entity Usage\n")
        report.append("| Entity Type | Count |")
        report.append("|-------------|-------|")
        
        for entity, count in sorted(
            stats["entities_usage"].items(), key=lambda x: x[1], reverse=True
        ):
            report.append(f"| `{entity}` | {count} |")
    
    # Slots usage
    if stats.get("slots_usage"):
        report.append("\n## 🗃️ Slot Usage\n")
        report.append("| Slot | Count |")
        report.append("|------|-------|")
        
        for slot, count in sorted(
            stats["slots_usage"].items(), key=lambda x: x[1], reverse=True
        ):
            report.append(f"| `{slot}` | {count} |")
    
    # Add visualization references
    if os.path.exists(PLOTS_DIR):
        report.append("\n## 📈 Visualizations\n")
        for img in ["intent_distribution.png", "conversation_lengths.png", 
                   "entity_usage.png", "messages_by_hour.png"]:
            img_path = os.path.join(PLOTS_DIR, img)
            if os.path.exists(img_path):
                report.append(f"### {img.replace('.png', '').replace('_', ' ').title()}")
                report.append(f"![{img}]({img_path})\n")
    
    return "\n".join(report)


def main():
    """Main function to run the analysis."""
    print("🔍 Loading conversation data...")
    conversations = load_conversations()
    
    if not conversations:
        print("❌ No conversation data found or error loading data.")
        return
    
    print("📊 Analyzing conversations...")
    stats = analyze_conversations(conversations)
    
    if not stats:
        print("❌ No conversation data to analyze.")
        return
    
    print("📈 Creating visualizations...")
    create_visualizations(stats)
    
    print("📝 Generating report...")
    report = generate_report(stats)
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Analysis complete! Report saved to {REPORT_FILE}")
    print(f"📊 Visualizations saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
