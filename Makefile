all: install
	pip install wheel
	python setup.py sdist bdist_wheel

install:
	pip install -e .

format:
	black . -l 79

test:
	policyengine-core test policyengine_uk/tests/policy -c policyengine_uk
	pytest policyengine_uk/tests/

test-setup:
	policyengine-core data enhanced_frs download 2022 -c policyengine_uk

documentation:
	jb clean docs/book
	jb build docs/book
	python policyengine_uk/tools/add_plotly_to_book.py docs/book/_build

changelog:
	build-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from 0.1.0 --append-file changelog_entry.yaml
	build-changelog changelog.yaml --org PolicyEngine --repo openfisca-uk --output CHANGELOG.md --template .github/changelog_template.md
	bump-version changelog.yaml setup.py
	rm changelog_entry.yaml || true
	touch changelog_entry.yaml
