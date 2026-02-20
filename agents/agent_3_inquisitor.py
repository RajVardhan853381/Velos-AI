"""
Agent 3: The Inquisitor
Verifies candidate authenticity through technical questions.
Catches resume fraud by deep-diving into claimed projects.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None


class Inquisitor:
    """
    Agent 3: The Inquisitor
    
    Responsibilities:
    1. Generate technical questions about claimed projects
    2. Evaluate candidate answers for authenticity
    3. Detect potential fraud/exaggeration
    4. Provide final authenticity score
    
    Key principle: Verify candidates actually did what they claim.
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key and ChatGroq:
            self.llm = ChatGroq(
                temperature=0.7,  # More creative for varied, unique questions
                api_key=api_key,  # type: ignore[arg-type]
                model="llama-3.3-70b-versatile"  # Updated from decommissioned llama-3.1-70b
            )
        else:
            self.llm = None
        
        self.audit_log = []
        self.questions_generated = []
        self.authenticity_threshold = 70  # Minimum score to pass
    
    def generate_technical_questions(self, clean_data: Dict, 
                                      num_questions: int = 3) -> List[str]:
        """
        Generate tough but fair technical questions about candidate's projects.
        Questions designed to expose if they didn't actually do the work.
        """
        
        projects = clean_data.get("projects", [])
        skills = clean_data.get("skills", [])
        
        # Default questions if no projects
        if not projects and not skills:
            return [
                "Tell us about the most challenging technical project you've worked on.",
                "Describe a problem you solved using your technical skills.",
                "What was your approach to learning a new technology recently?"
            ]
        
        if self.llm:
            prompt = f"""You are a technical interviewer verifying candidate authenticity.

Candidate's claimed skills: {', '.join(skills[:10])}
Candidate's claimed projects: {', '.join(str(p)[:100] for p in projects[:5])}

Generate {num_questions} TOUGH but FAIR technical questions to verify they actually did this work.

Focus on:
1. Implementation details (architecture decisions, specific challenges)
2. Problem-solving (bugs encountered, how they debugged)
3. Technology choices (why specific tech stack, trade-offs considered)

Questions should:
- Be specific enough to expose fakes
- Be fair to genuine candidates
- Not require memorizing documentation
- Focus on real-world experience

Return ONLY the questions, one per line, numbered 1., 2., 3.
Do NOT include explanations or notes."""

            try:
                response = self.llm.invoke(prompt)
                content = str(response.content).strip()
                
                # Parse questions from response
                lines = content.split('\n')
                questions = []
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Remove numbering
                        q = re.sub(r'^[\d\.\-\*\)]+\s*', '', line).strip()
                        if q and len(q) > 20:
                            questions.append(q)
                
                if questions:
                    self.questions_generated = questions[:num_questions]
                    return self.questions_generated
            except Exception as e:
                print(f"⚠️ LLM question generation failed: {e}")
        
        # Fallback: Generate template questions
        return self._generate_fallback_questions(skills, projects, num_questions)
    
    def _generate_fallback_questions(self, skills: List[str], 
                                      projects: List[str],
                                      num_questions: int) -> List[str]:
        """Generate fallback questions without LLM"""
        
        templates = [
            "Describe the architecture of your most complex project. What were the main components?",
            "What was the biggest technical challenge you faced, and how did you solve it?",
            "Explain a debugging scenario where you had to trace through multiple layers.",
            "How did you handle data flow in your project? Walk us through the pipeline.",
            "What trade-offs did you consider when choosing your tech stack?",
            "Describe how you tested your implementation. What was your testing strategy?",
            "How did you optimize performance in your project? What metrics did you measure?",
            "Explain how you handled error cases and edge scenarios.",
        ]
        
        # Customize based on skills
        if 'python' in [s.lower() for s in skills]:
            templates.insert(0, "How did you structure your Python codebase? Explain your module organization.")
        if any('llm' in s.lower() or 'rag' in s.lower() for s in skills):
            templates.insert(0, "Walk us through your RAG implementation. How did you handle document chunking?")
        if any('aws' in s.lower() or 'cloud' in s.lower() for s in skills):
            templates.insert(0, "Describe your cloud architecture. How did you handle scaling and cost?")
        
        self.questions_generated = templates[:num_questions]
        return self.questions_generated
    
    def evaluate_answer(self, question: str, answer: str,
                       clean_data: Dict) -> Dict:
        """
        Evaluate a single answer for authenticity.
        
        Returns:
            {
                "authenticity_score": 0-100,
                "red_flags": [list of concerns],
                "verdict": "GENUINE" or "SUSPICIOUS",
                "explanation": str
            }
        """
        
        if not answer or len(answer.strip()) < 20:
            return {
                "authenticity_score": 10,
                "red_flags": ["Answer too short or empty"],
                "verdict": "SUSPICIOUS",
                "explanation": "Insufficient detail provided"
            }
        
        if self.llm:
            skills = clean_data.get("skills", [])
            projects = clean_data.get("projects", [])
            
            eval_prompt = f"""Evaluate this technical interview answer for AUTHENTICITY.

Question: {question}

Candidate's Answer: {answer}

Context - Claimed skills: {', '.join(skills[:8])}
Context - Claimed projects: {', '.join(str(p)[:50] for p in projects[:3])}

Evaluate on these criteria:
1. Technical accuracy (does answer show real understanding?)
2. Specificity (mentions actual technical details, not generic?)
3. Consistency (aligns with claimed skills/projects?)
4. Experience indicators (sounds like they've actually done this?)

Red flags to watch for:
- Vague, generic answers anyone could give
- Inconsistencies with claimed experience
- Textbook answers without practical insight
- Inability to explain trade-offs or challenges

Return ONLY valid JSON:
{{
    "authenticity_score": (0-100, where 100 is definitely genuine),
    "red_flags": ["list of specific concerns, empty if none"],
    "verdict": "GENUINE" or "SUSPICIOUS",
    "explanation": "brief explanation of your assessment"
}}"""

            try:
                response = self.llm.invoke(eval_prompt)
                content = str(response.content).strip()
                
                # Extract JSON
                if "{" in content and "}" in content:
                    json_start = content.index("{")
                    json_end = content.rindex("}") + 1
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Validate required fields
                    if "authenticity_score" in result:
                        return result
            except Exception as e:
                print(f"⚠️ Answer evaluation failed: {e}")
        
        # Fallback: Simple heuristic evaluation
        return self._evaluate_answer_heuristic(answer)
    
    def _evaluate_answer_heuristic(self, answer: str) -> Dict:
        """Fallback answer evaluation using heuristics"""
        
        score = 50  # Start at neutral
        red_flags = []
        
        # Positive signals
        if len(answer) > 200:
            score += 10  # Detailed answer
        if any(tech in answer.lower() for tech in ['because', 'trade-off', 'challenge', 'decided']):
            score += 10  # Shows reasoning
        if re.search(r'\d+', answer):
            score += 5  # Includes specific numbers
        if any(word in answer.lower() for word in ['implemented', 'built', 'designed', 'debugged']):
            score += 10  # Action-oriented language
        
        # Negative signals
        if len(answer) < 100:
            score -= 15
            red_flags.append("Answer lacks detail")
        if answer.lower().startswith(('i think', 'maybe', 'probably')):
            score -= 10
            red_flags.append("Uncertain language")
        if answer.count('.') < 2:
            score -= 10
            red_flags.append("Single sentence answer")
        
        score = max(0, min(100, score))
        
        return {
            "authenticity_score": score,
            "red_flags": red_flags,
            "verdict": "GENUINE" if score >= 60 else "SUSPICIOUS",
            "explanation": "Evaluated using heuristic analysis"
        }
    
    def _get_resume_context(self, query: str, vector_store: Any,
                            candidate_id: str) -> List[str]:
        """
        Query vector store for specific context from the resume.
        Returns relevant chunks for question generation.
        """
        if not vector_store or not candidate_id:
            return []
        
        try:
            results = vector_store.get_context_with_scores(
                query=query,
                candidate_id=candidate_id,
                k=3
            )
            
            # Return only relevant chunks (score > 0.3)
            return [chunk for chunk, score in results if score > 0.3]
        except Exception as e:
            print(f"⚠️ Vector store query failed: {e}")
            return []
    
    def generate_evidence_based_questions(self, clean_data: Dict,
                                          vector_store: Any,
                                          candidate_id: str,
                                          num_questions: int = 3) -> List[Dict]:
        """
        Generate targeted technical questions based on specific resume evidence.
        Each question includes the source citation.
        """
        
        questions_with_evidence = []
        
        # Query categories to mine from resume
        query_categories = [
            ("architecture", "architecture design system components"),
            ("challenges", "challenges problems solved difficulties"),
            ("engineering", "implementation built developed created"),
            ("optimization", "performance optimization scaling"),
            ("decisions", "decisions choices trade-offs selected")
        ]
        
        evidence_snippets = {}
        for category, query in query_categories:
            chunks = self._get_resume_context(query, vector_store, candidate_id)
            if chunks:
                evidence_snippets[category] = chunks[0][:300]  # First relevant chunk
        
        if evidence_snippets and self.llm:
            # Generate targeted questions based on specific evidence
            evidence_str = "\n".join([f"[{k}]: {v}" for k, v in evidence_snippets.items()])
            
            prompt = f"""You are a senior technical interviewer. Based on these SPECIFIC details from the candidate's resume, generate {num_questions} targeted verification questions.

Resume Evidence:
{evidence_str}

For each question:
1. Reference a SPECIFIC claim from the evidence
2. Ask for details only the actual implementer would know
3. Design to catch resume fraud (e.g., exaggerated contributions)

Format your response as:
1. [QUESTION]: <question text>
   [SOURCE]: <which part of resume this targets>

2. [QUESTION]: <question text>
   [SOURCE]: <which part of resume this targets>
"""
            
            try:
                response = self.llm.invoke(prompt)
                content = str(response.content).strip()
                
                # Parse questions with sources
                current_question = None
                current_source = None
                
                for line in content.split('\n'):
                    line = line.strip()
                    if '[QUESTION]:' in line or '[Question]:' in line.lower():
                        if current_question:
                            questions_with_evidence.append({
                                "question": current_question,
                                "source": current_source or "resume",
                                "type": "evidence-based"
                            })
                        current_question = re.sub(r'\[QUESTION\]:\s*', '', line, flags=re.IGNORECASE)
                    elif '[SOURCE]:' in line or '[Source]:' in line.lower():
                        current_source = re.sub(r'\[SOURCE\]:\s*', '', line, flags=re.IGNORECASE)
                
                # Add last question
                if current_question:
                    questions_with_evidence.append({
                        "question": current_question,
                        "source": current_source or "resume",
                        "type": "evidence-based"
                    })
                
            except Exception as e:
                print(f"⚠️ Evidence-based question generation failed: {e}")
        
        # If we don't have enough evidence-based questions, add general ones
        if len(questions_with_evidence) < num_questions:
            fallback = self.generate_technical_questions(clean_data, 
                                                         num_questions - len(questions_with_evidence))
            for q in fallback:
                questions_with_evidence.append({
                    "question": q,
                    "source": "general skills",
                    "type": "fallback"
                })
        
        return questions_with_evidence[:num_questions]
    
    def process(self, clean_data: Dict, num_questions: int = 3,
                vector_store: Any = None, candidate_id: str = "") -> Dict:
        """
        Generate verification questions for the candidate.
        Uses vector store for evidence-based question targeting.
        
        Args:
            clean_data: Anonymized data from Agent 1
            num_questions: Number of questions to generate
            vector_store: ResumeVectorStore instance for RAG
            candidate_id: Unique candidate identifier
        
        Returns:
            {
                "status": "READY",
                "questions": [list of questions],
                "questions_with_evidence": [list with citations],
                "audit_log": list
            }
        """
        
        # Reset audit log for this run
        self.audit_log = []

        audit_entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "Inquisitor",
            "action": "Generating evidence-based verification questions"
        }
        
        print("❓ Agent 3: Generating verification questions...")
        
        # Try evidence-based questions first
        if vector_store and candidate_id:
            print("   📚 Mining resume for specific details to verify...")
            questions_with_evidence = self.generate_evidence_based_questions(
                clean_data, vector_store, candidate_id, num_questions
            )
            
            questions = [q["question"] for q in questions_with_evidence]
            audit_entry["evidence_based"] = True
            audit_entry["questions_with_sources"] = questions_with_evidence
        else:
            questions = self.generate_technical_questions(clean_data, num_questions)
            questions_with_evidence = [{"question": q, "source": "general", "type": "fallback"} for q in questions]
            audit_entry["evidence_based"] = False
        
        audit_entry["questions_count"] = len(questions)
        audit_entry["questions"] = questions
        self.audit_log.append(audit_entry)
        
        return {
            "status": "READY",
            "questions": questions,
            "questions_with_evidence": questions_with_evidence,
            "audit_log": self.audit_log
        }
    
    def evaluate_candidate_answers(self, clean_data: Dict,
                                    qa_pairs: List[Dict]) -> Dict:
        """
        Evaluate all candidate answers and determine authenticity.
        
        Args:
            clean_data: Anonymized data from Agent 1
            qa_pairs: List of {"question": str, "answer": str}
            
        Returns:
            {
                "status": "PASS" or "FAIL",
                "reason": str,
                "authenticity_score": float (average),
                "individual_scores": list,
                "red_flags": list,
                "verdict": "GENUINE" or "SUSPICIOUS",
                "audit_log": list
            }
        """
        
        audit_entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "agent": "Inquisitor",
            "action": "Evaluating candidate answers"
        }
        
        print("❓ Agent 3: Evaluating answers for authenticity...")
        
        scores = []
        all_red_flags = []
        verdicts = []
        evaluations = []
        
        for i, qa in enumerate(qa_pairs):
            print(f"   Evaluating answer {i+1}/{len(qa_pairs)}...")
            
            evaluation = self.evaluate_answer(
                qa.get("question", ""),
                qa.get("answer", ""),
                clean_data
            )
            
            evaluations.append(evaluation)
            scores.append(evaluation.get("authenticity_score", 50))
            all_red_flags.extend(evaluation.get("red_flags", []))
            verdicts.append(evaluation.get("verdict", "UNCERTAIN"))
        
        # Calculate final score
        avg_score = sum(scores) / len(scores) if scores else 0
        genuine_count = verdicts.count("GENUINE")
        total_count = len(verdicts)
        
        audit_entry["individual_scores"] = scores
        audit_entry["average_score"] = avg_score
        audit_entry["red_flags"] = all_red_flags
        audit_entry["verdicts"] = verdicts
        audit_entry["evaluations"] = evaluations
        
        # Final decision
        # Pass if: avg score >= threshold AND at least half verdicts are GENUINE
        if avg_score >= self.authenticity_threshold and genuine_count >= total_count / 2:
            status = "PASS"
            reason = f"✅ Authentic: {avg_score:.0f}% confidence ({genuine_count}/{total_count} genuine)"
            final_verdict = "GENUINE"
            audit_entry["decision"] = "APPROVED"
        else:
            status = "FAIL"
            reason = f"❌ Low authenticity: {avg_score:.0f}% ({genuine_count}/{total_count} genuine)"
            final_verdict = "SUSPICIOUS"
            audit_entry["decision"] = "REJECTED"
            audit_entry["rejection_reason"] = "Failed authenticity check"
        
        self.audit_log.append(audit_entry)
        
        return {
            "status": status,
            "reason": reason,
            "authenticity_score": round(avg_score, 1),
            "individual_scores": scores,
            "red_flags": list(set(all_red_flags)),  # Unique flags
            "verdict": final_verdict,
            "evaluations": evaluations,
            "audit_log": self.audit_log
        }
    
    def get_audit_summary(self) -> str:
        """Generate human-readable audit summary"""
        if not self.audit_log:
            return "No processing done yet."
        
        latest = self.audit_log[-1]
        
        if latest.get("action") == "Generating verification questions":
            return f"""
❓ **Agent 3: Inquisitor - Questions Generated**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Questions**: {latest.get('questions_count', 0)} generated
**Status**: Awaiting candidate responses
"""
        else:
            return f"""
❓ **Agent 3: Inquisitor Audit**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Timestamp**: {latest.get('timestamp', 'N/A')}
**Decision**: {latest.get('decision', 'N/A')}
**Authenticity Score**: {latest.get('average_score', 0):.0f}%
**Individual Scores**: {latest.get('individual_scores', [])}
**Red Flags**: {len(latest.get('red_flags', []))}
**Verdicts**: {latest.get('verdicts', [])}
"""


# Quick test
if __name__ == "__main__":
    inquisitor = Inquisitor()
    
    # Simulated clean data
    clean_data = {
        "skills": ["python", "fastapi", "langchain", "rag", "aws"],
        "projects": [
            "Built RAG system for document Q&A using LangChain",
            "Developed REST API with FastAPI and PostgreSQL"
        ]
    }
    
    # Generate questions
    result = inquisitor.process(clean_data, num_questions=3)
    
    print("\n" + "="*50)
    print("AGENT 3: QUESTION GENERATION")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Questions generated: {len(result['questions'])}")
    for i, q in enumerate(result['questions'], 1):
        print(f"\n{i}. {q}")
    
    # Simulate answers and evaluate
    qa_pairs = [
        {
            "question": result['questions'][0] if result['questions'] else "Tell us about your project",
            "answer": "I built a RAG system using LangChain and Pinecone. The main challenge was optimizing chunk size for retrieval - I experimented with 500, 1000, and 1500 tokens and found 800 worked best for our use case. I also implemented a reranking step using cross-encoders which improved answer relevance by about 20%."
        },
        {
            "question": result['questions'][1] if len(result['questions']) > 1 else "Describe a challenge",
            "answer": "The biggest challenge was handling rate limits on the OpenAI API. I implemented exponential backoff and request queuing. We also added caching for frequently asked questions which reduced API costs by 40%."
        },
        {
            "question": result['questions'][2] if len(result['questions']) > 2 else "Explain your tech stack",
            "answer": "I chose FastAPI for the backend because of its async support and automatic OpenAPI documentation. For the vector store, Pinecone made sense because of its managed scaling. The trade-off was cost vs self-hosting something like Milvus."
        }
    ]
    
    eval_result = inquisitor.evaluate_candidate_answers(clean_data, qa_pairs)
    
    print("\n" + "="*50)
    print("AGENT 3: EVALUATION RESULT")
    print("="*50)
    print(f"Status: {eval_result['status']}")
    print(f"Authenticity Score: {eval_result['authenticity_score']}%")
    print(f"Verdict: {eval_result['verdict']}")
    print(f"Reason: {eval_result['reason']}")
    if eval_result['red_flags']:
        print(f"Red Flags: {eval_result['red_flags']}")
