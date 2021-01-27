# Copyright 2021 Sean Kelleher. All rights reserved.
# Use of this source code is governed by an MIT
# licence that can be found in the LICENCE file.

tgt_dir:=target
tgt_test_dir:=$(tgt_dir)/tests

.PHONY: check
check: \
		check_unit \
		check_intg \
		check_style

.PHONY: check_unit
check_unit:
	python3 \
		-m doctest \
		test_comment_style.py
	python3 test_comment_style.py

.PHONY: check_intg
check_intg: $(tgt_test_dir)
	bash scripts/test_intg.sh

.PHONY: check_style
check_style:
	pycodestyle \
		comment_style.py
	python3 comment_style.py \
		"comment_style.yaml"

# We tag `$(tgt_test_dir)` as phony so that the test directory is removed and
# recreated at the start of every test run.
.PHONY: $(tgt_test_dir)
$(tgt_test_dir): | $(tgt_dir)
	rm -rf '$(tgt_test_dir)'
	mkdir '$@'

$(tgt_dir):
	mkdir '$@'
