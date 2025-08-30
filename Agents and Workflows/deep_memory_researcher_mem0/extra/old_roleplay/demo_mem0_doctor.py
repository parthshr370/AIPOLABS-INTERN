#!/usr/bin/env python3

import os
import warnings
from dotenv import load_dotenv
from mem0 import MemoryClient
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.types import ModelPlatformType

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# API keys and configuration
DOCTOR_MEMORY_ID = "doctor_memory"  # Unified medical memory store
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

console = Console()
if not MEM0_API_KEY or not GOOGLE_API_KEY:
    console.print("[red]Error: Missing API keys in environment variables[/red]")
    exit(1)

# Initialize memory client
mem0 = MemoryClient()

# Initialize model
model = ModelFactory.create(
    model_platform=ModelPlatformType.GEMINI,
    model_type="gemini-2.5-flash",
    api_key=GOOGLE_API_KEY,
    model_config_dict={"temperature": 0.1, "max_tokens": 4096},
)

def run_medical_roleplay(patient_id: str = None, rounds: int = 8) -> list:
    """
    Function 1: Pure roleplay task - generates medical conversation
    Returns list of conversation exchanges for memory storage
    """
    # Generate unique patient ID if not provided
    if not patient_id:
        import random
        patient_names = ["Alex Thompson", "Maria Garcia", "James Wilson", "Sarah Johnson", "Michael Chen"]
        patient_id = f"patient_{random.choice(patient_names).replace(' ', '_').lower()}_{random.randint(1000,9999)}"
    
    rprint(f"[bold green]🏥 Generating COMPREHENSIVE Medical Consultation for {patient_id}...[/bold green]")
    
    # COMPREHENSIVE Medical Consultation - Real Clinical Detail
    medical_context = f"""
    COMPREHENSIVE MEDICAL CONSULTATION PROTOCOL for {patient_id}:
    
    DOCTOR must conduct DETAILED clinical assessment including:
    
    1. CHIEF COMPLAINT & HPI:
    - Primary complaint with SOAP format: "52yo male presents with 3-day history of substernal chest pain, 7/10 severity, radiating to left arm and jaw, worse with exertion, associated with diaphoresis and nausea. Pain lasts 10-15 minutes, relieved by rest."
    
    2. VITAL SIGNS & PHYSICAL EXAM:
    - Complete vitals: "BP 148/92 mmHg (Stage 1 HTN), HR 84 bpm regular, RR 18/min, Temp 98.4°F, O2 sat 97% RA, BMI 28.3 kg/m²"
    - Physical findings: "Heart: RRR, no murmurs/gallops, PMI non-displaced. Lungs: CTAB, no rales/wheeze. Extremities: no edema, pulses 2+ bilaterally"
    
    3. LABORATORY & DIAGNOSTIC DATA:
    - Recent labs: "Lipid panel: TC 245 mg/dL, LDL 165 mg/dL, HDL 38 mg/dL, TG 210 mg/dL. BMP: Glucose 142 mg/dL, Cr 1.1 mg/dL, eGFR >60. CBC: WBC 7.2K, Hgb 13.8 g/dL, Plt 285K"
    - Imaging: "ECG shows normal sinus rhythm, no acute ST changes. CXR clear."
    
    4. ASSESSMENT & CLINICAL REASONING:
    - Primary diagnosis with ICD-10: "Unstable Angina, I20.0" or "NSTEMI, I21.9" 
    - Secondary diagnoses: "Hypertension I10, Dyslipidemia E78.5, Tobacco Use Disorder Z87.891"
    - Risk stratification: "TIMI score 4 (moderate risk), Framingham 10-year CVD risk 18%"
    
    5. TREATMENT PLAN with SPECIFICS:
    - Medications: "Aspirin 81mg daily, Atorvastatin 80mg HS, Metoprolol XL 50mg daily, Lisinopril 10mg daily"
    - Lifestyle: "Smoking cessation counseling, cardiac diet <2g sodium, exercise as tolerated"
    - Follow-up: "Cardiology consult within 1 week, lipid recheck in 6 weeks, BP monitoring"
    
    PATIENT must provide COMPREHENSIVE history:
    - Detailed symptoms with quality, timing, severity, aggravating/alleviating factors
    - Complete medication list with dosages and adherence
    - Family history: "Father MI age 58, mother HTN/DM2 age 65, brother stroke age 60"
    - Social history: "Smokes 1 PPD x 25 years (25 pack-years), drinks 2-3 beers nightly, desk job, no regular exercise"
    - Review of systems: Specific yes/no responses to cardiovascular, pulmonary, GI symptoms
    """
    
    # Setup RolePlaying with memory-enhanced context
    medical_meta_dict = {
        "assistant_role": "Dr. Sarah Chen (Internal Medicine Physician)",
        "user_role": "Alex Thompson (45-year-old office worker patient)",
        "task": medical_context
    }
    
    society = RolePlaying(
        task_prompt=f"Conduct COMPREHENSIVE medical consultation for {patient_id} with detailed clinical assessment, extensive history taking, physical examination findings, laboratory interpretation, clinical reasoning, and complete treatment planning",
        with_task_specify=False,
        assistant_role_name="Dr. Sarah Chen, Internal Medicine",
        user_role_name=f"{patient_id.replace('_', ' ').title()}, Patient",
        assistant_agent_kwargs={"model": model},
        user_agent_kwargs={"model": model},
        extend_sys_msg_meta_dicts=[medical_meta_dict, medical_meta_dict]
    )
    
    # Collect conversation exchanges
    conversation_log = []
    input_msg = society.init_chat()
    
    for round_num in range(rounds):
        assistant_response, user_response = society.step(input_msg)
        
        if assistant_response.terminated or user_response.terminated:
            break
            
        # Log the exchange with patient ID for tracking
        exchange = {
            "round": round_num + 1,
            "patient_id": patient_id,
            "patient_message": user_response.msg.content,
            "doctor_message": assistant_response.msg.content,
            "timestamp": round_num + 1,
            "consultation_type": "comprehensive_medical_evaluation"
        }
        conversation_log.append(exchange)
        
        # Display for monitoring
        rprint(f"[blue]👤 Patient:[/blue] {user_response.msg.content[:100]}...")
        rprint(f"[red]👨‍⚕️ Doctor:[/red] {assistant_response.msg.content[:100]}...")
        
        if "CAMEL_TASK_DONE" in user_response.msg.content:
            break
            
        input_msg = assistant_response.msg
    
    rprint(f"[green]✅ Generated {len(conversation_log)} conversation exchanges[/green]")
    return conversation_log

def store_medical_memories(conversation_log: list, doctor_memory_id: str) -> dict:
    """
    Function 2: Memory operations - processes and stores conversation data
    Returns memory storage statistics
    """
    rprint("[bold yellow]💾 Processing Medical Memories...[/bold yellow]")
    
    stored_memories = []
    memory_stats = {
        "total_exchanges": len(conversation_log),
        "stored_memories": 0,
        "medical_entities": []
    }
    
    for exchange in conversation_log:
        # Format each exchange as a conversation pair for mem0 with patient tracking
        patient_name = exchange['patient_id'].replace('patient_', '').replace('_', ' ').title()
        conversation_pair = [
            {
                "role": "user", 
                "content": f"Patient {patient_name} [{exchange['patient_id']}]: {exchange['patient_message']}"
            },
            {
                "role": "assistant", 
                "content": f"Dr. Sarah Chen consulting {patient_name} [{exchange['patient_id']}]: {exchange['doctor_message']}"
            }
        ]
        
        # Store in mem0 under unified doctor memory
        try:
            mem0.add(messages=conversation_pair, user_id=doctor_memory_id)
            stored_memories.append(f"Round {exchange['round']}: Patient symptoms & Doctor diagnosis")
            memory_stats["stored_memories"] += 1
            
            # Extract medical entities for tracking
            doctor_msg = exchange['doctor_message'].lower()
            patient_msg = exchange['patient_message'].lower()
            
            # Comprehensive medical entity detection
            if any(term in doctor_msg for term in ['mmhg', 'blood pressure', 'bp', 'hr', 'bpm', 'temp', 'o2 sat']):
                memory_stats["medical_entities"].append("Vital Signs")
            if any(term in doctor_msg for term in ['mg/dl', 'glucose', 'hba1c', 'lipid', 'cholesterol', 'lab', 'cbc']):
                memory_stats["medical_entities"].append("Laboratory Values")
            if any(term in doctor_msg for term in ['mg', 'medication', 'prescrib', 'daily', 'bid', 'hs']):
                memory_stats["medical_entities"].append("Medication Prescription")
            if any(term in patient_msg for term in ['/10', 'pain', 'severity', 'sharp', 'dull', 'radiating']):
                memory_stats["medical_entities"].append("Symptom Assessment")
            if any(term in doctor_msg for term in ['icd', 'diagnos', 'i10', 'i20', 'e11', 'e78']):
                memory_stats["medical_entities"].append("ICD-10 Diagnosis")
            if any(term in doctor_msg for term in ['physical exam', 'heart', 'lungs', 'rrr', 'ctab', 'murmur']):
                memory_stats["medical_entities"].append("Physical Examination")
            if any(term in patient_msg for term in ['family history', 'father', 'mother', 'brother', 'sister']):
                memory_stats["medical_entities"].append("Family History")
            if any(term in patient_msg for term in ['smoke', 'drink', 'alcohol', 'exercise', 'pack', 'years']):
                memory_stats["medical_entities"].append("Social History")
            if any(term in doctor_msg for term in ['ecg', 'ekg', 'chest x-ray', 'cxr', 'imaging']):
                memory_stats["medical_entities"].append("Diagnostic Studies")
                
        except Exception as e:
            rprint(f"[red]Error storing memory for round {exchange['round']}: {e}[/red]")
    
    # Remove duplicates from medical entities
    memory_stats["medical_entities"] = list(set(memory_stats["medical_entities"]))
    
    rprint(f"[green]✅ Stored {memory_stats['stored_memories']} medical memory exchanges[/green]")
    return memory_stats

def check_memory_status(doctor_memory_id: str) -> int:
    """
    Simple check to see how many memories are stored (optional)
    """
    try:
        memories = mem0.search(query="medical", user_id=doctor_memory_id, limit=50)
        return len(memories) if memories else 0
    except:
        return 0

def main():
    """
    Main loop: Orchestrates roleplay generation and memory storage
    """
    console.print(Panel(
        "[bold blue]🏥 COMPREHENSIVE Medical Consultation Memory System[/bold blue]\n\n"
        "Generates DETAILED doctor-patient conversations with comprehensive\n"
        "clinical assessments and feeds them into unified doctor_memory.\n\n"
        "Commands:\n"
        "• 'consult [patient_name]' - Generate comprehensive consultation (8+ rounds)\n"
        "• 'consult' - Generate consultation with random patient\n"
        "• 'status' - Check memory count in doctor_memory store\n"
        "• 'reset' - Clear all medical memories\n"
        "• 'exit' - Quit system\n\n"
        "[dim]Example: 'consult john_doe' or just 'consult'[/dim]",
        title="🩺 Demo Mem0 Doctor System",
        border_style="green"
    ))
    
    while True:
        try:
            user_input = console.input("\n[bold cyan]Command:[/bold cyan] ").strip()
            command_parts = user_input.lower().split()
            
            if command_parts[0] in ['exit', 'quit']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
                
            elif command_parts[0] == 'reset':
                console.print("[bold yellow]🗑️ Clearing all medical memories...[/bold yellow]")
                mem0.delete_all(user_id=DOCTOR_MEMORY_ID)
                console.print("[green]✅ Medical memories cleared.[/green]")
                
            elif command_parts[0] == 'status':
                console.print("[bold blue]📊 Checking memory status...[/bold blue]")
                memory_count = check_memory_status(DOCTOR_MEMORY_ID)
                console.print(f"[green]💾 Current memories stored: {memory_count}[/green]")
                
            elif command_parts[0] == 'consult':
                # Extract patient name if provided
                patient_id = None
                if len(command_parts) > 1:
                    patient_name = '_'.join(command_parts[1:])
                    patient_id = f"patient_{patient_name}"
                
                # Generate comprehensive roleplay conversation (8 rounds)
                console.print("[bold magenta]🚀 Generating COMPREHENSIVE medical consultation...[/bold magenta]")
                conversation_log = run_medical_roleplay(patient_id=patient_id, rounds=8)
                
                if conversation_log:
                    # Store in unified doctor memory
                    memory_stats = store_medical_memories(conversation_log, DOCTOR_MEMORY_ID)
                    
                    # Display comprehensive summary
                    patient_info = conversation_log[0]['patient_id'] if conversation_log else "Unknown"
                    summary = f"""
                    📊 **COMPREHENSIVE Consultation Summary:**
                    👤 Patient ID: {patient_info}
                    🗣️  Generated {memory_stats['total_exchanges']} detailed conversation rounds
                    💾 Stored {memory_stats['stored_memories']} medical memories successfully
                    🏥 Medical entities captured: {', '.join(memory_stats['medical_entities']) if memory_stats['medical_entities'] else 'None detected'}
                    
                    💡 **Clinical Data Stored:**
                    • Comprehensive patient history and symptoms
                    • Detailed physical examination findings  
                    • Laboratory values and diagnostic studies
                    • ICD-10 diagnoses and clinical reasoning
                    • Specific medication prescriptions with dosing
                    • Treatment plans and follow-up recommendations
                    
                    🗄️  All data integrated into unified doctor_memory knowledge base
                    """
                    console.print(Panel(summary, title="✅ Memory Storage Complete", border_style="green"))
                else:
                    console.print("[red]❌ No conversation generated.[/red]")
                    
            else:
                console.print("[yellow]Available commands: consult [patient_name], status, reset, exit[/yellow]")
                console.print("[dim]Example: 'consult john_smith' or just 'consult' for random patient[/dim]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    main()