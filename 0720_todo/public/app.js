const form = document.getElementById("task-form");
const titleInput = document.getElementById("title");
const dueDateInput = document.getElementById("due_date");
const list = document.getElementById("task-list");

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

function renderTask(task) {
  const li = document.createElement("li");
  li.className = "task" + (task.is_done ? " done" : "");

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = task.is_done;
  checkbox.addEventListener("change", () => toggleDone(task.id, checkbox.checked));
  li.appendChild(checkbox);

  const title = document.createElement("div");
  title.className = "task-title";
  title.textContent = task.title;
  li.appendChild(title);

  if (task.due_date) {
    const badge = document.createElement("span");
    const overdue = !task.is_done && task.due_date < todayStr();
    badge.className = "due-badge" + (overdue ? " overdue" : "");
    badge.textContent = `마감 ${task.due_date}`;
    li.appendChild(badge);
  }

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "delete-btn";
  deleteBtn.textContent = "✕";
  deleteBtn.setAttribute("aria-label", "삭제");
  deleteBtn.addEventListener("click", () => deleteTask(task.id));
  li.appendChild(deleteBtn);

  return li;
}

async function loadTasks() {
  const res = await fetch("/api/tasks");
  const tasks = await res.json();
  list.innerHTML = "";
  if (tasks.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-state";
    empty.textContent = "할 일이 없습니다.";
    list.appendChild(empty);
    return;
  }
  for (const task of tasks) {
    list.appendChild(renderTask(task));
  }
}

async function toggleDone(id, isDone) {
  await fetch(`/api/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_done: isDone }),
  });
  loadTasks();
}

async function deleteTask(id) {
  await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  loadTasks();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = titleInput.value.trim();
  if (!title) return;

  await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title,
      due_date: dueDateInput.value || null,
    }),
  });

  form.reset();
  loadTasks();
});

loadTasks();
