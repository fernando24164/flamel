# Build directory
BUILD = build

# Distribution directory
DIST = dist

create:
	python3 -m pip install --upgrade build
	python3 -m build
	pip install .

clean:
	rm -rf $(BUILD) $(DIST)
	
# Phony targets
PHONY: create clean