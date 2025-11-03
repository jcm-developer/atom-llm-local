import matplotlib
matplotlib.use('Agg')  # GUI-less backend for servers
import matplotlib.pyplot as plt
import json
import re

def parse_data_from_text(text):
    """
    Attempts to extract structured data from the model's response text.
    Searches for common patterns like lists, tables, or JSON.
    
    Args:
        text: Model text that may contain data
        
    Returns:
        dict: Dictionary with 'labels' and 'values' or None if extraction fails
    """
    # Clean the text of markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try to find JSON in the text
    # First search for the most common pattern: {...}
    json_match = re.search(r'\{[^{}]*\}', text)
    
    if json_match:
        try:
            json_str = json_match.group()
            data = json.loads(json_str)
            
            if isinstance(data, dict) and len(data) > 0:
                # Assume the dict has format {label: value}
                labels = []
                values = []
                
                for key, value in data.items():
                    labels.append(str(key))
                    # Try to convert the value to a number
                    try:
                        if isinstance(value, (int, float)):
                            values.append(float(value))
                        elif isinstance(value, str):
                            # Try to extract number from strings
                            num_match = re.search(r'(\d+\.?\d*)', value)
                            if num_match:
                                values.append(float(num_match.group(1)))
                            else:
                                values.append(len(value))
                        else:
                            values.append(1)
                    except (ValueError, AttributeError):
                        values.append(1)
                
                if labels and values:
                    return {'labels': labels, 'values': values}
                    
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing JSON: {e}")
            pass
    
    # If simple JSON not found, search for arrays of objects
    array_match = re.search(r'\[[\s\S]*\]', text)
    if array_match:
        try:
            data = json.loads(array_match.group())
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    # List of objects
                    first_key = list(data[0].keys())[0]
                    second_key = list(data[0].keys())[1] if len(data[0].keys()) > 1 else first_key
                    return {
                        'labels': [str(item.get(first_key, '')) for item in data],
                        'values': [float(item.get(second_key, 0)) if isinstance(item.get(second_key), (int, float)) else 1 for item in data]
                    }
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
    
    # Search for table patterns with numbers
    lines = text.split('\n')
    labels = []
    values = []
    
    for line in lines:
        # Search for lines with format "Label: Number" or "Label | Number" or "Label - Number"
        match = re.search(r'([^:|–-]+)[:|\–-]\s*(\d+\.?\d*)', line)
        if match:
            labels.append(match.group(1).strip())
            values.append(float(match.group(2)))
        else:
            # Search for lines with numbers at the end
            match = re.search(r'(.+?)\s+(\d+\.?\d*)$', line.strip())
            if match and len(line.strip()) > 3:
                labels.append(match.group(1).strip())
                values.append(float(match.group(2)))
    
    if labels and values and len(labels) == len(values):
        return {'labels': labels, 'values': values}
    
    return None


def generate_chart(filepath, content, chart_type='bar'):
    """
    Generates a chart from data extracted from the content.
    
    Args:
        filepath: Path where the image will be saved
        content: Text containing the data (can be JSON, table, or text with data)
        chart_type: Type of chart ('bar', 'line', 'pie', 'scatter')
    """
    print(f"\n=== GENERATING CHART ===")
    print(f"Type: {chart_type}")
    print(f"Content received: {content[:300]}...")
    
    # Style configuration
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Try to extract data from content
    data = parse_data_from_text(content)
    
    if not data:
        print("❌ Could not extract data from content")
        # If data cannot be extracted, create an example chart
        data = {
            'labels': ['No data', 'available'],
            'values': [1, 1]
        }
        ax.text(0.5, 0.5, 'Could not extract structured data\n\nPlease provide data in format:\nJSON: {"2020": 50000, "2021": 55000, "2022": 60000}\n\nReceived response:\n' + content[:200], 
                ha='center', va='center', fontsize=10, transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), wrap=True)
        plt.axis('off')
    else:
        print(f"✅ Data extracted correctly:")
        print(f"   Labels: {data['labels']}")
        print(f"   Values: {data['values']}")
        
        labels = data['labels']
        values = data['values']
        
        # Generate chart according to type
        if chart_type == 'bar':
            bars = ax.bar(labels, values, color='steelblue', alpha=0.8, edgecolor='black')
            ax.set_ylabel('Values', fontsize=12, fontweight='bold')
            ax.set_xlabel('Categories', fontsize=12, fontweight='bold')
            ax.set_title('Bar Chart', fontsize=16, fontweight='bold', pad=20)
            
            # Rotate labels if there are many or they're very long
            if len(labels) > 5 or any(len(str(l)) > 10 for l in labels):
                plt.xticks(rotation=45, ha='right')
            
            # Add values on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=10)
        
        elif chart_type == 'line':
            ax.plot(labels, values, marker='o', linewidth=2, markersize=8, 
                   color='steelblue', markerfacecolor='orange', markeredgecolor='black')
            ax.set_ylabel('Values', fontsize=12, fontweight='bold')
            ax.set_xlabel('Categories', fontsize=12, fontweight='bold')
            ax.set_title('Line Chart', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            
            if len(labels) > 5 or any(len(str(l)) > 10 for l in labels):
                plt.xticks(rotation=45, ha='right')
        
        elif chart_type == 'pie':
            colors = plt.cm.Set3(range(len(labels)))
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                              colors=colors, startangle=90,
                                              textprops={'fontsize': 10})
            ax.set_title('Pie Chart', fontsize=16, fontweight='bold', pad=20)
            
            # Improve readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        elif chart_type == 'scatter':
            ax.scatter(range(len(values)), values, s=100, alpha=0.6, 
                      c='steelblue', edgecolors='black', linewidth=1.5)
            ax.set_ylabel('Values', fontsize=12, fontweight='bold')
            ax.set_xlabel('Index', fontsize=12, fontweight='bold')
            ax.set_title('Scatter Plot', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            
            # Add labels
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels)
            if len(labels) > 5 or any(len(str(l)) > 10 for l in labels):
                plt.xticks(rotation=45, ha='right')
    
    # Adjust layout so labels don't get cut off
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(str(filepath), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
