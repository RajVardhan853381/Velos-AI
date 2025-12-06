#!/usr/bin/env python3
"""
Velos - Memory Layer Test Script
Tests the Vector Database (RAG) functionality.

This verifies:
1. Resume can be stored (chunked + embedded)
2. Relevant context can be retrieved via semantic search
3. Security filtering works (can't access other candidates' data)

Built for ZYND AIckathon 2025
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.vector_store import ResumeVectorStore


def test_memory_layer():
    """Test the vector store memory layer."""
    
    print("=" * 60)
    print("🧪 Velos Memory Layer Test")
    print("=" * 60)
    
    # Initialize
    print("\n📦 Initializing Vector Store...")
    store = ResumeVectorStore()
    
    if not store.is_available:
        print("❌ Vector store not available. Check dependencies.")
        return False
    
    print(f"✅ Vector store ready")
    print(f"   📊 Stats: {store.get_stats()}")
    
    # Test Resume 1: Python/Django Developer
    test_resume_1 = """
    PROFESSIONAL SUMMARY
    I have 5 years of experience in Python and built a Django app for e-commerce.
    Led a team of 4 developers to create a microservices architecture on AWS.
    
    TECHNICAL SKILLS
    - Languages: Python, JavaScript, SQL, Go
    - Frameworks: Django, FastAPI, React, Node.js
    - Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB, Redis
    
    WORK EXPERIENCE
    
    Senior Software Engineer | TechCorp Inc. | 2020 - Present
    - Architected and deployed a high-traffic e-commerce platform using Django
    - Implemented CI/CD pipelines reducing deployment time by 70%
    - Mentored junior developers and conducted code reviews
    
    Software Engineer | StartupAI | 2018 - 2020
    - Built RESTful APIs serving 1M+ daily requests
    - Developed real-time analytics dashboard using React and D3.js
    
    EDUCATION
    M.S. Computer Science | Stanford University | 2018
    B.S. Computer Science | UC Berkeley | 2016
    """
    
    # Test Resume 2: ML Engineer (different person)
    test_resume_2 = """
    MACHINE LEARNING ENGINEER
    
    Experienced ML engineer with focus on computer vision and NLP.
    Built production ML systems at scale using TensorFlow and PyTorch.
    
    SKILLS
    - ML Frameworks: TensorFlow, PyTorch, scikit-learn, Keras
    - Languages: Python, C++, CUDA
    - MLOps: MLflow, Kubeflow, Weights & Biases
    - Cloud: GCP (Vertex AI, BigQuery), AWS SageMaker
    
    EXPERIENCE
    
    ML Engineer | AICompany | 2019 - Present
    - Developed object detection models with 95% accuracy for autonomous vehicles
    - Built NLP pipeline for sentiment analysis processing 10K documents/hour
    - Deployed models using TensorFlow Serving and Kubernetes
    
    Research Assistant | MIT CSAIL | 2017 - 2019
    - Published 3 papers on deep learning for medical imaging
    - Developed novel attention mechanisms for transformer models
    """
    
    # Test 1: Add resumes
    print("\n" + "-" * 40)
    print("TEST 1: Adding resumes to vector store")
    print("-" * 40)
    
    result1 = store.add_resume("test_user_1", test_resume_1)
    print(f"📝 Added test_user_1: {result1}")
    
    result2 = store.add_resume("test_user_2", test_resume_2)
    print(f"📝 Added test_user_2: {result2}")
    
    if not result1.get("success") or not result2.get("success"):
        print("❌ Failed to add resumes")
        return False
    
    print("✅ Both resumes stored successfully")
    
    # Test 2: Search for Django (should find in user 1)
    print("\n" + "-" * 40)
    print("TEST 2: Semantic search for 'Django experience'")
    print("-" * 40)
    
    context = store.get_context("Django web development experience", "test_user_1")
    print(f"🔍 Query: 'Django web development experience' for test_user_1")
    print(f"📄 Result: {context[:300]}..." if len(context) > 300 else f"📄 Result: {context}")
    
    if "Django" in context or "django" in context.lower():
        print("✅ Found Django experience in correct user's resume")
    else:
        print("⚠️ Django not found - may need to check chunking")
    
    # Test 3: Search for TensorFlow (should find in user 2)
    print("\n" + "-" * 40)
    print("TEST 3: Semantic search for 'machine learning TensorFlow'")
    print("-" * 40)
    
    context2 = store.get_context("machine learning TensorFlow models", "test_user_2")
    print(f"🔍 Query: 'machine learning TensorFlow models' for test_user_2")
    print(f"📄 Result: {context2[:300]}..." if len(context2) > 300 else f"📄 Result: {context2}")
    
    if "TensorFlow" in context2 or "ML" in context2 or "machine learning" in context2.lower():
        print("✅ Found ML/TensorFlow in correct user's resume")
    else:
        print("⚠️ TensorFlow not found - may need to check chunking")
    
    # Test 4: Security - Search wrong user (should return nothing)
    print("\n" + "-" * 40)
    print("TEST 4: Security test - cross-user access prevention")
    print("-" * 40)
    
    wrong_context = store.get_context("Django", "test_user_2")
    print(f"🔒 Query: 'Django' for test_user_2 (shouldn't have Django)")
    print(f"📄 Result: '{wrong_context[:100]}'" if wrong_context else "📄 Result: (empty)")
    
    if "Django" not in wrong_context and "django" not in wrong_context.lower():
        print("✅ SECURITY PASS: Cannot access other user's Django data")
    else:
        print("❌ SECURITY FAIL: Found Django in wrong user's results!")
    
    # Test 5: Search non-existent user
    print("\n" + "-" * 40)
    print("TEST 5: Search for non-existent user")
    print("-" * 40)
    
    no_context = store.get_context("Python", "nonexistent_user")
    print(f"🔍 Query: 'Python' for nonexistent_user")
    print(f"📄 Result: '{no_context}'" if no_context else "📄 Result: (empty)")
    
    if not no_context:
        print("✅ Correctly returned empty for non-existent user")
    else:
        print("⚠️ Unexpected data returned for non-existent user")
    
    # Test 6: Get detailed results with scores
    print("\n" + "-" * 40)
    print("TEST 6: Retrieve with similarity scores")
    print("-" * 40)
    
    detailed = store.get_context_with_scores("cloud infrastructure AWS", "test_user_1")
    print(f"🔍 Query: 'cloud infrastructure AWS' for test_user_1")
    for i, chunk in enumerate(detailed):
        print(f"   Chunk {i+1}: distance={chunk['distance']:.4f}")
        print(f"            text: {chunk['text'][:100]}...")
    
    # Test 7: Stats
    print("\n" + "-" * 40)
    print("TEST 7: Vector store statistics")
    print("-" * 40)
    
    stats = store.get_stats()
    print(f"📊 Stats: {stats}")
    
    # Cleanup (optional - comment out to persist data)
    # print("\n🧹 Cleaning up test data...")
    # store.delete_candidate("test_user_1")
    # store.delete_candidate("test_user_2")
    
    print("\n" + "=" * 60)
    print("✅ All memory layer tests completed!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_memory_layer()
    sys.exit(0 if success else 1)
