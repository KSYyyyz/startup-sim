.PHONY: format lint test playtest docs-check check

# 代码格式化
format:
	python -m black . --line-length 100 --target-version py311
	python -m isort . --profile black --line-length 100

# 静态检查
lint:
	python -m ruff check .

# 运行测试
test:
	python -m pytest tests/ -v

# 试玩脚本
playtest:
	python scripts/playtest.py

# 文档一致性检查
docs-check:
	python scripts/check_docs_consistency.py

# 质量门（版本推进前必须通过）
check: format lint test playtest docs-check
	@echo "All checks passed."
