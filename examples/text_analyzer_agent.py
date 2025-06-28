"""
Example: Text Analyzer Agent with A2A Protocol and LangGraph Workflow

This demonstrates how to create an A2A agent that uses LangGraph workflows
with custom functions that call LLMs and MCP tools.
"""

from typing import Dict, Any
from langgraph import StateGraph
from langgraph.graph import MessagesState

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.a2a_agent import A2AAgent


class TextAnalyzerAgent(A2AAgent):
    """
    A2A Agent that analyzes text using LLM + MCP tools via LangGraph workflow.
    
    Workflow:
    1. Receive text input
    2. Use LLM to analyze sentiment and extract entities
    3. Use MCP tool to enhance analysis
    4. Format and return results
    """
    
    # A2A Agent Card properties
    capabilities = ["text_analysis", "sentiment_analysis", "entity_extraction"]
    supported_modalities = ["text", "json"]
    version = "1.0.0"
    description = "Text analysis agent with LLM and MCP integration"
    
    def build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow for text analysis.
        
        The workflow contains custom functions that call LLMs and MCP tools.
        """
        # Define custom state
        class AnalysisState(MessagesState):
            text_input: str = ""
            llm_analysis: Dict[str, Any] = {}
            mcp_enhancement: Dict[str, Any] = {}
            final_result: Dict[str, Any] = {}
        
        # Create workflow
        workflow = StateGraph(AnalysisState)
        
        # Add custom function nodes
        workflow.add_node("extract_text", self.extract_text)
        workflow.add_node("llm_analysis", self.analyze_with_llm)
        workflow.add_node("mcp_enhancement", self.enhance_with_mcp)
        workflow.add_node("format_response", self.format_final_response)
        
        # Define workflow flow
        workflow.add_edge("extract_text", "llm_analysis")
        workflow.add_edge("llm_analysis", "mcp_enhancement")
        workflow.add_edge("mcp_enhancement", "format_response")
        
        # Set entry and exit points
        workflow.set_entry_point("extract_text")
        workflow.set_finish_point("format_response")
        
        return workflow
    
    # Custom workflow functions
    async def extract_text(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from input messages."""
        messages = state.get("messages", [])
        if messages:
            text_input = messages[-1].get("content", "") if isinstance(messages[-1], dict) else str(messages[-1])
        else:
            text_input = ""
        
        self.logger.info(f"📝 Extracting text: {text_input[:50]}...")
        
        return {"text_input": text_input}
    
    async def analyze_with_llm(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Custom function that calls LLM for text analysis."""
        text_input = state.get("text_input", "")
        
        if not text_input:
            return {"llm_analysis": {"error": "No text to analyze"}}
        
        self.logger.info("🧠 Analyzing text with LLM...")
        
        try:
            # Use the helper method to call LLM
            prompt = f"""
            Analyze the following text and provide:
            1. Sentiment (positive/negative/neutral)
            2. Key entities mentioned
            3. Main topics
            4. Confidence score (0-1)
            
            Text: {text_input}
            
            Respond in JSON format.
            """
            
            llm_response = await self.llm_call(prompt)
            
            # Parse LLM response (in real implementation, you'd want better parsing)
            llm_analysis = {
                "llm_response": llm_response,
                "sentiment": "positive",  # Would extract from LLM response
                "entities": ["example", "entity"],
                "topics": ["analysis", "text"],
                "confidence": 0.85,
                "analyzed_text_length": len(text_input)
            }
            
            self.logger.info(f"✅ LLM analysis completed: {llm_analysis['sentiment']} sentiment")
            
            return {"llm_analysis": llm_analysis}
            
        except Exception as e:
            self.logger.error(f"❌ LLM analysis failed: {e}")
            return {"llm_analysis": {"error": str(e)}}
    
    async def enhance_with_mcp(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Custom function that calls MCP tool for enhancement."""
        text_input = state.get("text_input", "")
        llm_analysis = state.get("llm_analysis", {})
        
        self.logger.info("🔧 Enhancing analysis with MCP tools...")
        
        try:
            # Use the helper method to call MCP tool
            mcp_result = await self.mcp_call("text_enhancer", {
                "text": text_input,
                "initial_analysis": llm_analysis
            })
            
            mcp_enhancement = {
                "mcp_result": mcp_result,
                "enhancement_type": "detailed_analysis",
                "additional_insights": ["enhanced", "analysis"],
                "processing_time": 0.1
            }
            
            self.logger.info("✅ MCP enhancement completed")
            
            return {"mcp_enhancement": mcp_enhancement}
            
        except Exception as e:
            self.logger.warning(f"⚠️ MCP enhancement failed: {e}")
            # Graceful degradation - continue without MCP
            return {"mcp_enhancement": {"error": str(e), "fallback": True}}
    
    async def format_final_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Custom function that formats the final response."""
        text_input = state.get("text_input", "")
        llm_analysis = state.get("llm_analysis", {})
        mcp_enhancement = state.get("mcp_enhancement", {})
        
        self.logger.info("📋 Formatting final response...")
        
        # Combine all analysis results
        final_result = {
            "input_text": text_input,
            "analysis": {
                "sentiment": llm_analysis.get("sentiment", "unknown"),
                "entities": llm_analysis.get("entities", []),
                "topics": llm_analysis.get("topics", []),
                "confidence": llm_analysis.get("confidence", 0.0)
            },
            "enhancement": {
                "mcp_available": "error" not in mcp_enhancement,
                "additional_insights": mcp_enhancement.get("additional_insights", [])
            },
            "metadata": {
                "agent_id": self.agent_id,
                "workflow_completed": True,
                "processing_steps": ["llm_analysis", "mcp_enhancement", "formatting"]
            }
        }
        
        # Create response message
        response_content = f"""
Text Analysis Complete:

📝 Text: {text_input[:100]}...
😊 Sentiment: {final_result['analysis']['sentiment']}
🏷️  Entities: {', '.join(final_result['analysis']['entities'])}
📊 Confidence: {final_result['analysis']['confidence']:.2f}
🔧 MCP Enhanced: {final_result['enhancement']['mcp_available']}
        """.strip()
        
        return {
            "final_result": final_result,
            "response": response_content,
            "messages": state.get("messages", []) + [
                {"role": "assistant", "content": response_content}
            ]
        }


# Example usage
async def main():
    """Example usage of TextAnalyzerAgent."""
    print("🚀 Starting Text Analyzer Agent Example")
    
    # Create agent with configuration
    agent = TextAnalyzerAgent(
        agent_id="text_analyzer_001",
        config={
            "llm_model": "gpt-4o-mini",
            "llm_temperature": 0.3,
            "mcp_server_url": "http://localhost:8080"
        }
    )
    
    # Initialize agent
    await agent.initialize()
    
    # Test A2A Agent Card
    agent_card = agent.get_agent_card()
    print("📋 Agent Card:")
    print(f"   Agent ID: {agent_card['agent_id']}")
    print(f"   Capabilities: {agent_card['capabilities']}")
    print(f"   Workflow Enabled: {agent_card['metadata']['workflow_enabled']}")
    
    # Test message processing through workflow
    test_message = "I love this new AI technology! It's amazing how it can analyze text and provide insights."
    
    print(f"\\n📝 Processing message: {test_message}")
    print("-" * 50)
    
    # Process message through A2A agent workflow
    async for result in agent.stream(test_message, session_id="demo_session"):
        if result.get("success"):
            print(f"✅ Result: {result.get('content', 'No content')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\\n🎉 Example completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
