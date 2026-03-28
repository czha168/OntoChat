"""
Main application for OntoChat.
Supports configuration-based LLM provider access with health checks on startup.
"""
import sys
import gradio as gr

from ontochat.config_loader import load_config, ConfigurationError
from ontochat.health_check import run_health_check, HealthCheckError
from ontochat.functions import user_story_generator, load_example


user_story_template = """**Persona:**

- Name: -
- Age: -
- Occupation: -
- Skills: -
- Interests: -

**Goal:**

- Description: -
- Keywords: -

**Scenario:**

- Before: -
- During: -
- After: -

**Example Data:**

- Category: -
- Data: -

**Resources:**

- Resource Name: -
- Link: -"""

current_preidentified = [
    """The ontology's domain is **[DOMAIN]**.

    Ensure all subsequent responses strictly adhere to the scope of my domain. Use ontology-specific terminology and align responses with relevant ontological structures, relationships, and reasoning principles.""",
       
    """My persona is **[NAME]**, I am **[AGE]** years old, and I work as a **[OCCUPATION]** in the domain of **[DOMAIN]**. My expertise includes **[SKILLS]**, and I have a strong interest in **[INTERESTS]**.

    Please refine my response to ensure:

    1. The persona is clearly described with a focus on ontology-related expertise.
    2. The details (name, age, occupation, skills, interests) are logically aligned with domain ontologies and structured knowledge representation.
    3. If the skills and interests provided by the user are similar and hard to differentiate, generate distinct ones by distinguishing between conceptual knowledge (e.g., ontological modeling) and applied techniques (e.g., knowledge graph construction).
    4. The language is *[CONCISE & PRECISE / CREATIVE & DETAILED]*, ensuring clarity in an ontology-driven context.
    5. The final answer is structured as *[BULLET POINTS / A DETAILED PARAGRAPH]*.""",
]


with gr.Blocks() as user_story_interface:
    gr.Markdown(
        """
        # Welcome to OntoChat! 👋

        Hi there! I'm OntoChat, your conversational assistant for collaborative ontology engineering. 

        📋 I assist with ontology requirements elicitation by asking targeted questions, collecting user inputs, providing example answers, and recommending prompt templates to guide you.

        📝 I offer customizable prompts designed for different interaction stages, ensuring structured guidance throughout the process.

        ⚙️ You can edit placeholders within these templates to refine constraints and shape my responses to fit your specific needs.

        🔄 I continuously improve my responses based on your feedback until you're satisfied.

        Let's make ontology development smoother and more interactive! 🚀

        For more details, visit 🌐 [OntoChat on GitHub](https://github.com/King-s-Knowledge-Graph-Lab/OntoChat).
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            user_story_chatbot = gr.Chatbot(
                value=[
                    {"role": "assistant", "content": (
                        "Hello! I'm OntoChat 😊. I'll help you create an ontology user story!\n\n"
                        "1. I will ask you one **elicitation question** at a time, present an **example answer** to support your understanding, and recommend a **prompt template** 📄 for answering.\n\n"
                        "2. Don't worry about prompting—find the **template** 📄 I recommended and edit the **placeholders** 📝 to craft an effective response 👍.\n\n"
                        "3. Within a prompt template:\n"
                        "   - **\\*\\*[]\\*\\*** placeholders are **mandatory**.\n"
                        "   - **\\*[]\\*** placeholders are **optional**.\n\n"
                        "4. I will **refine** my generation iteratively based on your input 🔄 until you are satisfied ✅.\n\n"
                        "Let's get started! **Which domain is this ontology for?**\n\n"
                        "**For example:** *Healthcare, Wine, Music, etc.*\n\n"
                        "Use template **[Create Domain]** to answer. 🚀"
                    )}
                ],
                height="472px"
            )
            user_story_input = gr.Textbox(
                label="Message OntoChat",
                placeholder="Please type your message here and press Enter to interact with the chatbot:",
                max_lines=20,
                lines=1
            )
            elicitation_questions_dataset = gr.Dataset(
                components=[user_story_input],
                label="Prompt Templates",
                type="index",
                samples=[
                    ["Create Domain"],
                    ["Create Persona"],
                    ["Create User Goal"],
                    ["Create Actions"],
                    ["Create Keywords"],
                    ["Create Current Methods"],
                    ["Create Challenges"],
                    ["Create New Methods"],
                    ["Create Outcomes"]
                ],
                samples_per_page=10
            )

    user_story_input.submit(
        fn=user_story_generator,
        inputs=[user_story_input, user_story_chatbot],
        outputs=[user_story_chatbot, user_story_input]
    )
    elicitation_questions_dataset.click(
        fn=load_example,
        inputs=[elicitation_questions_dataset],
        outputs=[user_story_input]
    )


demo = gr.TabbedInterface(
    [user_story_interface],
    ["User Story Generation"]
)


def main():
    """Main entry point for OntoChat."""
    try:
        # Load configuration
        config = load_config()
        print(f"✓ Configuration loaded: provider={config.provider.name}, model={config.provider.default_model}")
        
        # Run health checks
        try:
            run_health_check()
            print("✓ Health check passed - provider is ready")
        except HealthCheckError as e:
            print(f"❌ Health check failed: {e}")
            print("\nPlease fix the configuration and try again.")
            sys.exit(1)
        except ConfigurationError as e:
            print(f"❌ Configuration error: {e}")
            print("Please fix the errors above and create a valid config.toml file.")
            sys.exit(1)
            
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\nTo set up OntoChat:")
        print("1. Copy config.sample.toml to config.toml")
        print("2. Edit config.toml with your provider settings")
        print("3. Set environment variables for API keys (e.g., OPENAI_API_KEY)")
        sys.exit(1)


if __name__ == "__main__":
    main()
    demo.launch(share=True)
