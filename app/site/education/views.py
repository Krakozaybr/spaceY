from flask import (
    Blueprint,
    abort,
    render_template,
    request,
    jsonify,
    redirect,
)
from flask_login import current_user, login_required
from sqlalchemy import true

import settings
from app.models.db_session import create_session
from app.models.task import Task
from app.models.task_progress import TaskProgress
from app.models.users.user import User
from app.site.auth.decorators import professor_required, student_required
from app.site.education.forms import (
    VideoTaskForm,
    TestTaskForm,
    ImageTaskForm,
    TextTaskForm,
)
from app.utils.utils import (
    save_video,
    save_image,
    ImageFormatException,
    VideoFormatException,
    delete_img,
    delete_video,
)

site = Blueprint("education_site", __name__, template_folder=settings.TEMPLATES_DIR)
api = Blueprint("education_api", __name__)

blueprint = Blueprint("education", __name__, template_folder=settings.TEMPLATES_DIR)
blueprint.register_blueprint(api)
blueprint.register_blueprint(site)

current_user: User


@site.route("/tasks")
@login_required
def tasks():
    with create_session() as session:
        if current_user.is_student:
            progresses = session.query(TaskProgress).filter(
                TaskProgress.state.in_([TaskProgress.STARTED, TaskProgress.VISIBLE])
            )

            tasks = [p.task for p in progresses]
            data = {"tasks": tasks}
        else:
            data = {
                "tasks": session.query(Task)
                .filter(Task.user_id == current_user.id)
                .all()
            }
        return render_template("education/tasks.html", **data)


def fill_task(task, form):
    task.title = form.title.data
    task.description = form.description.data
    task.value = form.estimation.data

    if isinstance(form, VideoTaskForm):
        try:
            filename = save_video(form.video.data)
        except VideoFormatException:
            return "Неподдерживаемый формат"

        if task.video:
            delete_video(task.video)

        task.video = filename
    elif isinstance(form, TextTaskForm):
        task.text = form.text.data
    elif isinstance(form, TestTaskForm):
        task.question = form.question.data
    else:
        try:
            filename = save_image(form.image.data)
        except ImageFormatException:
            return "Неподдерживаемый формат"

        if task.image:
            delete_img(task.image)

        task.image = filename


@site.route("/create_task", methods=["POST", "GET"])
@professor_required
@login_required
def create_task():
    video_form = VideoTaskForm()
    text_form = TextTaskForm()
    test_form = TestTaskForm()
    image_form = ImageTaskForm()

    data = {
        "video_form": video_form,
        "text_form": text_form,
        "test_form": test_form,
        "image_form": image_form,
    }

    video = video_form.validate_on_submit()
    text = text_form.validate_on_submit()
    image = image_form.validate_on_submit()
    test = test_form.validate_on_submit()

    if not (video or test or text or image):
        return render_template("education/create_task.html", **data)

    with create_session() as session:

        task = Task()

        task.user = current_user

        if video:
            if err := fill_task(task, video_form):
                data["err"] = err
                return render_template("education/create_task.html", **data)
        elif text:
            fill_task(task, text_form)
        elif test:
            fill_task(task, test_form)
        elif image:
            if err := fill_task(task, image_form):
                data["err"] = err
                return render_template("education/create_task.html", **data)

        session.add(task)
        session.commit()
        session.refresh(task)

        return redirect(task.url)


@api.route("/api/delete_task/<int:pk>", methods=["POST"])
@professor_required
@login_required
def delete_task(pk):
    with create_session() as session:
        task: Task = session.query(Task).filter(Task.id == pk).first()

        if task is None:
            abort(404)

        if task.user_id != current_user.id:
            abort(403)

        session.delete(task)
        session.commit()

        return jsonify({}), 200


@site.route("/task/<int:pk>", methods=["POST", "GET"])
@login_required
def task_info(pk):
    with create_session() as session:

        task: Task = session.query(Task).filter(Task.id == pk).first()

        if task is None:
            abort(404)

        if current_user.is_student:

            task_progress: TaskProgress = (
                session.query(TaskProgress)
                .filter(
                    TaskProgress.task_id == task.id,
                    TaskProgress.user_id == current_user.id,
                )
                .first()
            )

            if task_progress is None:
                abort(404)

            if task_progress.state is TaskProgress.NOT_VISIBLE:
                abort(403)

            if task_progress.state == TaskProgress.VISIBLE:
                task_progress.state = TaskProgress.STARTED
                session.add(task_progress)
                session.commit()
                session.refresh(task_progress)
                session.refresh(task)

            data = {"task": task, "task_progress": task_progress}

            if task.video is not None:
                return render_template("education/student_video_task.html", **data)
            elif task.text is not None:
                return render_template("education/student_text_task.html", **data)
            elif task.question is not None:
                return render_template("education/student_test_task.html", **data)
            return render_template("education/student_image_task.html", **data)

        # Professor

        if task.video is not None:
            form = VideoTaskForm()
        elif task.text is not None:
            form = TextTaskForm()
        elif task.question is not None:
            form = TestTaskForm()
        else:
            form = ImageTaskForm()

        data = dict()

        if form.validate_on_submit():
            err = fill_task(task, form)

            if err:
                data["err"] = err
            else:
                session.add(task)
                session.commit()
                session.refresh(task)

        students = {
            student: None
            for student in session.query(User).filter(
                User.professor_id == current_user.id
            )
        }

        for progress in session.query(TaskProgress).filter(
            TaskProgress.task_id == task.id
        ):
            progress: TaskProgress
            students[progress.user] = progress

        for student in students:
            if students[student] is None:
                progress = TaskProgress()
                progress.user = student
                progress.task = task
                students[student] = progress
                session.add(progress)

        session.commit()

        data.update(
            {
                "task": task,
                "progresses": session.query(TaskProgress)
                .filter(
                    TaskProgress.state != TaskProgress.NOT_VISIBLE,
                    TaskProgress.task_id == task.id,
                )
                .all(),
                "students_dont_see": session.query(TaskProgress)
                .filter(
                    TaskProgress.state == TaskProgress.NOT_VISIBLE,
                    TaskProgress.task_id == task.id,
                )
                .all(),
                "form": form,
            }
        )

        fields = {
            "title": task.title,
            "description": task.description,
            "estimation": task.value,
            "video": task.video,
            "text": task.text,
            "question": task.question,
            "image": task.image,
        }

        for key, val in fields.items():
            if hasattr(form, key):
                getattr(form, key).data = val

        return render_template("education/task_info.html", **data)


@api.route("/api/set_visibility", methods=["POST"])
@professor_required
@login_required
def set_visibility():
    try:
        user_id = int(request.json.get("user_id"))
        task_id = int(request.json.get("task_id"))
        state = bool(request.json.get("state"))
    except (KeyError, ValueError):
        abort(400)

    with create_session() as session:

        user = (
            session.query(User)
            .filter(
                User.id == user_id,
                User.is_student == true(),
                User.professor_id == current_user.id,
            )
            .first()
        )

        if user is None:
            abort(404)

        task = (
            session.query(Task)
            .filter(
                Task.id == task_id,
                Task.user_id == current_user.id,
            )
            .first()
        )

        if task is None:
            abort(404)

        task_progress = (
            session.query(TaskProgress)
            .filter(TaskProgress.user_id == user.id, TaskProgress.task_id == task.id)
            .first()
        )

        if task_progress.state in [TaskProgress.SENT, TaskProgress.CHECKED]:
            abort(406)

        if task_progress is None:
            task_progress = TaskProgress()
            task_progress.user = user
            task_progress.task = task

        task_progress.state = (
            TaskProgress.VISIBLE if state else TaskProgress.NOT_VISIBLE
        )

        session.commit()
        session.refresh(task_progress)

        return jsonify({}), 200


@api.route("/api/submit_answer", methods=["POST"])
@student_required
@login_required
def submit_answer():
    try:
        task_id = int(request.json.get("task_id"))
        answer = request.json.get("choice")
    except (KeyError, ValueError):
        abort(400)

    with create_session() as session:
        task: Task = (
            session.query(Task)
            .filter(
                Task.id == task_id,
                Task.user_id == current_user.professor_id,
            )
            .first()
        )

        if task is None:
            abort(404)

        task_progress: TaskProgress = (
            session.query(TaskProgress)
            .filter(
                TaskProgress.user_id == current_user.id, TaskProgress.task_id == task.id
            )
            .first()
        )

        if task_progress is None or task_progress.state in [
            TaskProgress.NOT_VISIBLE,
            TaskProgress.SENT,
        ]:
            abort(403)

        if task_progress.task.question:
            task_progress.answer = answer
            task_progress.state = TaskProgress.SENT
        else:
            task_progress.state = TaskProgress.CHECKED
            task_progress.user.rating += task.value
            task_progress.estimation = task.value

        session.add(task_progress)
        session.commit()

    return jsonify({}), 200


@site.route("/progress/<int:pk>")
@professor_required
@login_required
def estimation(pk):
    with create_session() as session:
        progress: TaskProgress = (
            session.query(TaskProgress).filter(TaskProgress.id == pk).first()
        )

        if progress is None:
            abort(404)

        student: User = progress.user
        if current_user.id != student.professor_id:
            abort(403)

        data = {"progress": progress}

        return render_template("education/estimation.html", **data)


@api.route("/api/estimate/<int:pk>", methods=["POST"])
@professor_required
@login_required
def estimate(pk):
    try:
        estimation = int(request.json.get("estimation"))
    except (KeyError, ValueError):
        abort(400)

    with create_session() as session:
        progress: TaskProgress = (
            session.query(TaskProgress).filter(TaskProgress.id == pk).first()
        )

        if progress is None:
            abort(404)

        print(f"{progress.user.professor_id=}")
        print(f"{current_user.id=}")
        if progress.user.professor_id != current_user.id:
            abort(403)

        if estimation < 0 or estimation > progress.task.value:
            abort(400)

        progress.state = TaskProgress.CHECKED
        if progress.estimation:
            progress.user.rating -= progress.estimation
        progress.user.rating += estimation
        progress.estimation = estimation

        session.add(progress)
        session.commit()

        return jsonify({}), 200
