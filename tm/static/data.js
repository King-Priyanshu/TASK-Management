  async function fetchTaskData() {
    const response = await fetch("{% url 'myapp:get_task_data' %}");
    const data = await response.json();

    document.getElementById('completed-count').textContent = data.task_data.completed_count;
    document.getElementById('pending-count').textContent = data.task_data.pending_count;
    document.getElementById('total-count').textContent = data.task_data.total_tasks;
  }

  fetchTaskData(); // Call once
  setInterval(fetchTaskData, 30000);