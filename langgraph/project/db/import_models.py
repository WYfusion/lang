"""
模型导入脚本
==============

用于 Alembic `from base import Base` 场景下，确保所有 ORM 模型都被导入，
从而让 `Base.metadata` 包含完整表定义，支持 `--autogenerate`。
"""

from __future__ import annotations

from importlib import import_module


MODEL_MODULES = (
    "models.conversation",
    "models.message",
    "models.memory",
)


def import_all_model_modules() -> list[str]:
    """导入全部 ORM 模型模块，返回成功导入的模块名。"""
    imported: list[str] = []

    for module_name in MODEL_MODULES:
        try:
            import_module(module_name)
            imported.append(module_name)
            continue
        except ImportError:
            pass

        package_name = f"db.{module_name}"
        import_module(package_name)
        imported.append(package_name)

    return imported
