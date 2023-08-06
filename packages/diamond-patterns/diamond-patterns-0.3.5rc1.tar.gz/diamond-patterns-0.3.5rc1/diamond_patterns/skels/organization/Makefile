# Organization Makefile

all:
	@echo OK

bill:
	_bin/new_bill.py

minutes:
	_bin/new_minutes.py

post:
	_bin/new_post.py

depends:
	bundle install --path vendor/bundle

serve:
	bundle exec jekyll serve

incremental:
	bundle exec jekyll clean
	bundle exec jekyll serve --incremental

build:
	JEKYLL_ENV=production bundle exec jekyll build

production:
	JEKYLL_ENV=production bundle exec jekyll serve

.PHONY: all bill minutes post depends serve incremental build production
