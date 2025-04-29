from datetime import UTC, datetime

from celery import states  # type: ignore

from models.base import Base

from .engine import db


class CeleryTask(Base):
    """
    Task result/status.
    
    Celery任务结果/状态
    
    存储异步任务的执行状态和结果信息。
    每条记录对应一个Celery异步任务的完整生命周期数据。
    """

    __tablename__ = "celery_taskmeta"

    id = db.Column(db.Integer, db.Sequence("task_id_sequence"), primary_key=True, autoincrement=True)  # 主键ID
    task_id = db.Column(db.String(155), unique=True)  # 任务唯一标识符
    status = db.Column(db.String(50), default=states.PENDING)  # 任务状态(PENDING, SUCCESS, FAILURE等)
    result = db.Column(db.PickleType, nullable=True)  # 序列化的任务结果
    date_done = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=True,
    )  # 任务完成时间
    traceback = db.Column(db.Text, nullable=True)  # 错误追踪信息(如有)
    name = db.Column(db.String(155), nullable=True)  # 任务名称
    args = db.Column(db.LargeBinary, nullable=True)  # 序列化的任务参数
    kwargs = db.Column(db.LargeBinary, nullable=True)  # 序列化的任务关键字参数
    worker = db.Column(db.String(155), nullable=True)  # 执行任务的工作节点
    retries = db.Column(db.Integer, nullable=True)  # 重试次数
    queue = db.Column(db.String(155), nullable=True)  # 任务所在队列


class CeleryTaskSet(Base):
    """
    TaskSet result.
    
    Celery任务集结果
    
    存储一组相关任务(任务集)的聚合结果。
    用于管理和跟踪由多个相关子任务组成的复杂任务流程。
    """

    __tablename__ = "celery_tasksetmeta"

    id = db.Column(db.Integer, db.Sequence("taskset_id_sequence"), autoincrement=True, primary_key=True)  # 主键ID
    taskset_id = db.Column(db.String(155), unique=True)  # 任务集唯一标识符
    result = db.Column(db.PickleType, nullable=True)  # 序列化的任务集结果
    date_done = db.Column(db.DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=True)  # 完成时间
