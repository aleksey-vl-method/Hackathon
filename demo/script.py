
#!/usr/bin/env python3
"""
Comprehensive Phishing Email Generator
Combines JIRA API functionality, ticket storage, and GPT-4 phishing email generation
"""

import os
import sys
import glob
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add parent directory to path to import jiralib and linkly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jiralib import get_jira_connection, get_active_jira_issues_by_email, extract_issue_details
from linkly import create_linkly_oneshot_link

# OpenAI imports
from openai import OpenAI


class PhishingEmailGenerator:
    """Main class that combines JIRA API, ticket storage, and GPT-4 generation"""
    
    def __init__(self):
        """Initialize the generator with API clients"""
        load_dotenv()
        self.openai_client = self.setup_openai_client()
        self.jira_tickets = []
        self.context = ""
        # Load Linkly credentials from environment
        self.linkly_email = os.getenv("LINKLY_EMAIL")
        self.linkly_api_key = os.getenv("LINKLY_API_KEY")
        self.linkly_workspace_id = os.getenv("LINKLY_WORKSPACE_ID")
        
    def setup_openai_client(self):
        """Setup OpenAI client with API key from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return OpenAI(api_key=api_key)
    
    def fetch_jira_tickets(self, email: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch JIRA tickets for a specific user and store as JSON objects
        
        Args:
            email: Email address of the assignee
            max_results: Maximum number of tickets to fetch
            
        Returns:
            List of ticket dictionaries
        """
        print(f"Fetching JIRA tickets for: {email}")
        
        try:
            tickets = get_active_jira_issues_by_email(email, max_results)
            self.jira_tickets = tickets
            
            if tickets:
                print(f"✓ Fetched {len(tickets)} active JIRA tickets")
                for ticket in tickets:
                    print(f"  - {ticket['key']}: {ticket['summary']}")
            else:
                print("No active tickets found")
                
            return tickets
            
        except Exception as e:
            print(f"Error fetching JIRA tickets: {str(e)}")
            return []
    
    def load_prompts_context(self, prompts_dir: str = "./prompts") -> str:
        """
        Load context from prompts directory, prioritizing context files
        
        Args:
            prompts_dir: Path to prompts directory
            
        Returns:
            Combined context string
        """
        context_parts = []
        
        if not os.path.exists(prompts_dir):
            print(f"Prompts directory '{prompts_dir}' not found.")
            return ""
        
        pattern = os.path.join(prompts_dir, "*.txt")
        txt_files = glob.glob(pattern)
        
        if not txt_files:
            print(f"No .txt files found in '{prompts_dir}'")
            return ""
        
        # Sort files to prioritize those with "context" in the name
        context_files = [f for f in txt_files if "context" in os.path.basename(f).lower()]
        other_files = [f for f in txt_files if "context" not in os.path.basename(f).lower()]
        
        # Prioritize context files first, then other files
        sorted_files = context_files + other_files
        
        print(f"Loading context from {len(sorted_files)} files:")
        if context_files:
            print(f"  Prioritizing {len(context_files)} context file(s) first")
        
        context_parts.append("=== CONTEXT INFORMATION ===")
        
        total_chars = 0
        max_context_chars = 90000  # Limit for GPT-4 Turbo
        
        for file_path in sorted_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    filename = os.path.basename(file_path)
                    content = f.read().strip()
                    if content:
                        # Check if adding this content would exceed our limit
                        if total_chars + len(content) > max_context_chars:
                            remaining_chars = max_context_chars - total_chars
                            if remaining_chars > 100:
                                content = content[:remaining_chars] + "... [truncated]"
                            else:
                                print(f"  ⚠ {filename} skipped (would exceed context limit)")
                                continue
                        
                        priority_marker = " [PRIORITY]" if "context" in filename.lower() else ""
                        context_parts.append(f"\n--- {filename.upper()}{priority_marker} ---")
                        context_parts.append(content)
                        total_chars += len(content)
                        print(f"  ✓ {filename} ({len(content)} characters){priority_marker}")
                    else:
                        print(f"  ⚠ {filename} (empty file)")
            except Exception as e:
                print(f"  ✗ Error reading {file_path}: {str(e)}")
        
        context_parts.append("\n=== END OF CONTEXT ===\n")
        
        print(f"Total context loaded: {total_chars} characters")
        self.context = "\n".join(context_parts)
        return self.context
    
    def create_jira_tickets_context(self) -> str:
        """
        Convert JIRA tickets to context string with comprehensive details
        
        Returns:
            Formatted JIRA tickets context
        """
        if not self.jira_tickets:
            print("⚠ No JIRA tickets available for context")
            return ""
        
        context_parts = []
        context_parts.append("=== RECENT JIRA TICKETS FOR TARGET USER ===")
        context_parts.append(f"Total Active Tickets: {len(self.jira_tickets)}")
        context_parts.append("")
        
        for i, ticket in enumerate(self.jira_tickets[:5], 1):  # Limit to 5 most recent
            context_parts.append(f"TICKET #{i}: {ticket['key']}")
            context_parts.append(f"Summary: {ticket['summary']}")
            context_parts.append(f"Status: {ticket['status']}")
            context_parts.append(f"Priority: {ticket['priority']}")
            context_parts.append(f"Issue Type: {ticket['issue_type']}")
            context_parts.append(f"Assignee: {ticket['assignee']}")
            context_parts.append(f"Reporter: {ticket['reporter']}")
            context_parts.append(f"Project: {ticket['project_name']} ({ticket['project_key']})")
            context_parts.append(f"Created: {ticket['created']}")
            context_parts.append(f"Updated: {ticket['updated']}")
            
            if ticket['description']:
                context_parts.append(f"Description: {ticket['description']}")
            
            if ticket['labels']:
                context_parts.append(f"Labels: {', '.join(ticket['labels'])}")
            
            if ticket['components']:
                context_parts.append(f"Components: {', '.join(ticket['components'])}")
            
            context_parts.append("---")
        
        if len(self.jira_tickets) > 5:
            context_parts.append(f"[Additional {len(self.jira_tickets) - 5} tickets not shown for brevity]")
        
        context_parts.append("=== END OF JIRA TICKETS ===\n")
        
        print(f"✓ Created JIRA context with {len(self.jira_tickets)} tickets")
        return "\n".join(context_parts)
    
    def generate_phishing_email(self, target_email: str, impersonate: str = "", 
                              model: str = "gpt-4-turbo") -> str:
        """
        Generate phishing email using GPT-4 with context and JIRA tickets
        
        Args:
            target_email: Email of the target user
            impersonate: Person to impersonate in the email
            model: OpenAI model to use
            
        Returns:
            Generated phishing email content
        """
        # Prepare the full context
        prompts_context = self.context if self.context else self.load_prompts_context()
        
        # Always create JIRA context from current tickets
        jira_context = self.create_jira_tickets_context()
        
        # Build the prompt
        base_prompt = "Generate a phishing email for cybersecurity awareness training"
        
        if impersonate:
            base_prompt += f" The email should appear to come from {impersonate}."
        
        if target_email:
            base_prompt += f" The target is {target_email}."
        
        # Combine all context - ensure JIRA tickets are always included
        full_prompt = f"{prompts_context}\n{jira_context}\n\nBased on the above organizational context and recent JIRA tickets, {base_prompt}"
        print(f"✓ Including {len(self.jira_tickets)} JIRA tickets in context")
        
     
        print(f"Generating phishing email...")
        print(f"Target: {target_email}")
        if impersonate:
            print(f"Impersonating: {impersonate}")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating phishing email: {str(e)}")
            return None
    
    def replace_links_with_linkly(self, phishing_email: str) -> str:
        """
        Replace all instances of LINK_HERE with actual Linkly shortened links
        
        Args:
            phishing_email: Email content with LINK_HERE placeholders
            
        Returns:
            Email content with real shortened links
        """
        if "LINK_HERE" not in phishing_email:
            print("⚠ No LINK_HERE placeholders found in email")
            return phishing_email
        
        # Check if Linkly credentials are available
        if not all([self.linkly_email, self.linkly_api_key, self.linkly_workspace_id]):
            print("⚠ Linkly credentials not found in environment variables")
            print("  Skipping link replacement. Please set LINKLY_EMAIL, LINKLY_API_KEY, and LINKLY_WORKSPACE_ID")
            return phishing_email
        
        # Convert workspace_id to int
        try:
            workspace_id = int(self.linkly_workspace_id)
        except ValueError:
            print("⚠ LINKLY_WORKSPACE_ID must be an integer")
            return phishing_email
        
        # Count placeholders
        placeholder_count = phishing_email.count("LINK_HERE")
        print(f"🔗 Found {placeholder_count} LINK_HERE placeholder(s)")
        
        # Create a Linkly shortened link
        print("🔗 Creating Linkly shortened link...")
        try:
            link_response = create_linkly_oneshot_link(
                email=self.linkly_email,
                api_key=self.linkly_api_key,
                workspace_id=workspace_id,
                url="https://www.method.me"
            )
            
            if link_response:
                short_url = link_response['full_url']
                
                # If we found a short URL, use it
                if short_url:
                    print(f"✓ Created shortened link: {short_url}")
                    
                    # Replace all instances of LINK_HERE with the shortened link
                    updated_email = phishing_email.replace("LINK_HERE", short_url)
                    print(f"✓ Replaced {placeholder_count} placeholder(s) with shortened link")
                    
                    return updated_email
                else:
                    print(f"⚠ Failed to find short URL in response. Response keys: {list(link_response.keys())}")
                    return phishing_email
            else:
                print("⚠ Failed to create Linkly link - no response received")
                return phishing_email
                
        except Exception as e:
            print(f"⚠ Error creating Linkly link: {str(e)}")
            return phishing_email
    
    def save_results(self, phishing_email: str, target_email: str, filename: str = None):
        """
        Save the generated results to file
        
        Args:
            phishing_email: Generated phishing email content
            target_email: Target email address
            filename: Optional custom filename
        """
        if not filename:
            filename = f"phishing_email_{target_email.replace('@', '_').replace('.', '_')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("PHISHING EMAIL GENERATOR RESULTS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Target Email: {target_email}\n")
                f.write(f"Generated on: {os.getcwd()}\n")
                f.write(f"JIRA Tickets Used: {len(self.jira_tickets)}\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("GENERATED PHISHING EMAIL:\n")
                f.write("-" * 30 + "\n")
                f.write(phishing_email)
                f.write("\n\n" + "=" * 50 + "\n\n")
                
                
            print(f"✓ Results saved to: {filename}")
            
        except Exception as e:
            print(f"✗ Error saving results: {str(e)}")

    def show_email_gui(self, phishing_email: str, target_email: str):
        """
        Display the generated phishing email in a Tkinter GUI
        
        Args:
            phishing_email: Generated phishing email content
            target_email: Target email address
        """
        root = tk.Tk()
        root.title("🎯 Phishing Email Training Viewer")
        root.geometry("900x700")
        root.configure(bg='#f0f0f0')
        
        # Extract subject from email if present
        subject_match = re.search(r'Subject: (.+)', phishing_email)
        subject = subject_match.group(1) if subject_match else "Phishing Email Training"
        
        # Header frame with email metadata
        header_frame = tk.Frame(root, bg='#dc3545', pady=15)
        header_frame.pack(fill='x')
        
        title_label = tk.Label(header_frame, text="🛡️ CYBERSECURITY TRAINING EMAIL", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#dc3545')
        title_label.pack()
        
        # Email metadata frame
        meta_frame = tk.Frame(root, bg='#e9ecef', pady=10)
        meta_frame.pack(fill='x')
        
        tk.Label(meta_frame, text=f"📧 To: {target_email}", 
                font=('Arial', 11, 'bold'), bg='#e9ecef').pack(anchor='w', padx=10)
        tk.Label(meta_frame, text=f"📋 Subject: {subject}", 
                font=('Arial', 11, 'bold'), bg='#e9ecef').pack(anchor='w', padx=10)
        tk.Label(meta_frame, text=f"📊 JIRA Tickets Used: {len(self.jira_tickets)}", 
                font=('Arial', 10), bg='#e9ecef', fg='#666').pack(anchor='w', padx=10)
        
        # Email content frame
        content_frame = tk.Frame(root, bg='white', pady=10)
        content_frame.pack(fill='both', expand=True, padx=10)
        
        tk.Label(content_frame, text="📬 Email Content:", 
                font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        # Scrollable text area for email content
        text_area = scrolledtext.ScrolledText(
            content_frame, 
            wrap=tk.WORD, 
            font=('Arial', 11),
            bg='white',
            fg='#333',
            selectbackground='#007bff',
            relief='sunken',
            borderwidth=2
        )
        text_area.pack(fill='both', expand=True, padx=5, pady=5)
        text_area.insert('1.0', phishing_email)
        text_area.config(state='disabled')  # Make read-only
        
        # Warning footer
        warning_frame = tk.Frame(root, bg='#fff3cd', pady=10)
        warning_frame.pack(fill='x')
        
        warning_text = "⚠️ TRAINING NOTICE: This is a simulated phishing email for cybersecurity awareness training purposes only."
        tk.Label(warning_frame, text=warning_text, 
                font=('Arial', 10, 'bold'), bg='#fff3cd', fg='#856404', 
                wraplength=800, justify='center').pack()
        
        # Buttons frame
        button_frame = tk.Frame(root, bg='#f0f0f0', pady=10)
        button_frame.pack(fill='x')
        
        # Close button
        tk.Button(button_frame, text="Close", command=root.destroy, 
                 bg='#6c757d', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side='right', padx=10)
        
        # Copy to clipboard button
        def copy_to_clipboard():
            root.clipboard_clear()
            root.clipboard_append(phishing_email)
            messagebox.showinfo("Copied", "Email content copied to clipboard!")
        
        tk.Button(button_frame, text="Copy Email", command=copy_to_clipboard,
                 bg='#007bff', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side='right', padx=5)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Start the GUI
        root.mainloop()


def main():
    """Main execution function"""
    print("🎯 Phishing Email Generator for Cybersecurity Training")
    print("=" * 60)
    
    # Initialize generator
    generator = PhishingEmailGenerator()
    
    # Input attack specifics
    target_email = input("Enter target email address: ").strip()
    if not target_email:
        target_email = "c.zhao@method.me"  # Default for testing
        print(f"Using default target: {target_email}")
    
    impersonate = input("Enter person to impersonate (optional): ").strip()
    prompts_folder = input("Enter prompts folder path (default: ./prompts): ").strip()
    if not prompts_folder:
        prompts_folder = "./prompts"
    
    print("\n" + "=" * 60)
    
    # Step 1: Fetch JIRA tickets
    print("STEP 1: Fetching JIRA tickets...")
    generator.fetch_jira_tickets(target_email, max_results=10)
    
    # Step 2: Load context from prompts
    print(f"\nSTEP 2: Loading context from '{prompts_folder}'...")
    generator.load_prompts_context(prompts_folder)
    
    # Step 3: Generate phishing email
    print("\nSTEP 3: Generating phishing email...")
    phishing_email = generator.generate_phishing_email(
        target_email=target_email,
        impersonate=impersonate
    )
    
    if phishing_email:
        # Step 3.5: Replace LINK_HERE placeholders with Linkly shortened links
        print("\nSTEP 3.5: Replacing link placeholders...")
        phishing_email = generator.replace_links_with_linkly(phishing_email)
        
        # Continue with the rest
        print("\n" + "=" * 60)
        print("GENERATED PHISHING EMAIL:")
        print("=" * 60)
        print(phishing_email)
        print("=" * 60)
        
        # Step 4: Save results
        print("\nSTEP 4: Saving results...")
        generator.save_results(phishing_email, target_email)
        
        # Step 5: Show email in GUI
        print("\nSTEP 5: Opening email viewer...")
        print("📧 Launching Tkinter GUI to display the phishing email...")
        generator.show_email_gui(phishing_email, target_email)
        
    else:
        print("✗ Failed to generate phishing email")


if __name__ == "__main__":
    main()