from core.care import CareCircle

def register_care_routes(router, ledger, auth_decorator):
    care = CareCircle(ledger)

    @router.get('/api/care/tasks')
    def list_tasks(h):
        h.send_json({"tasks": list(care.tasks.values())})

    @router.post('/api/care/verify')
    @auth_decorator
    def verify_care(h, user, p):
        task_id = p.get('task_id')
        quantity = float(p.get('quantity', 1.0))
        success, result = care.verify_care_labor(task_id, user['sub'], quantity)
        
        if success:
            h.send_json({
                "status": "success", 
                "reward": result,
                "message": f"Care labor verified. Received {result} AT."
            })
        else:
            h.send_json_error(result)

    # Seed initial care tasks
    @router.post('/api/care/seed_demo')
    @auth_decorator
    def seed_demo(h, user, p):
        care.add_task("Mentorship session", "Guidelines for onboarding new seekers.", 2.0)
        care.add_task("Wellness Check-in", "Verify the physical/mental readiness of a neighbor.", 1.0)
        care.add_task("Community Logistics", "Organizing the distribution of harvest surplus.", 1.5)
        h.send_json({"status": "success"})
