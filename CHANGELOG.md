# [0.6.0](https://github.com/smarter-sh/smarter-python/compare/v0.5.4...v0.6.0) (2026-10-26)


### Bug Fixes

* **models:** accept manifests with unquoted yaml dates ([5935456](https://github.com/smarter-sh/smarter-python/commit/593545628cd674f857b8723c1cb5a21d9fa0e665))


### Features

* re-export SAMKinds from smarter-types ([389ca4a](https://github.com/smarter-sh/smarter-python/commit/389ca4a5cb00374fa22bb20c1e1ce3a05419608b))

## [0.5.4](https://github.com/smarter-sh/smarter-python/compare/v0.5.3...v0.5.4) (2026-10-25)


### Bug Fixes

* **release:** publish the release's own build, not ci's ([03b2911](https://github.com/smarter-sh/smarter-python/commit/03b2911bb3e303616a000e3337094fbb27324f31))

## [0.5.4-alpha.1](https://github.com/smarter-sh/smarter-python/compare/v0.5.3...v0.5.4-alpha.1) (2026-10-25)


### Bug Fixes

* **release:** publish the release's own build, not ci's ([03b2911](https://github.com/smarter-sh/smarter-python/commit/03b2911bb3e303616a000e3337094fbb27324f31))

## [0.5.3](https://github.com/smarter-sh/smarter-python/compare/v0.5.2...v0.5.3) (2026-10-25)


### Bug Fixes

* **release:** release, publish and document the sdk like cache-results ([1696896](https://github.com/smarter-sh/smarter-python/commit/1696896b0bdda90da855db5bdc40a63e849767e7))
* **release:** start the release workflow on every push ([e4c9d36](https://github.com/smarter-sh/smarter-python/commit/e4c9d3614e3374a9cb8680cf33284a8744ce40be))

## [0.5.2](https://github.com/smarter-sh/smarter-python/compare/v0.5.1...v0.5.2) (2026-10-22)


### Bug Fixes

* **contracts:** sync with smarter v0.36.6 ([0aeb863](https://github.com/smarter-sh/smarter-python/commit/0aeb863976ee86ee658165fe42860d9e142f86b7))
* **llmclients:** add verbose option to config() ([55a93ff](https://github.com/smarter-sh/smarter-python/commit/55a93ffb3c4a306fda3102aacd00b903b1de7514))

## [0.5.1](https://github.com/smarter-sh/smarter-python/compare/v0.5.0...v0.5.1) (2026-10-15)


### Bug Fixes

* **contracts:** sync with smarter v0.27.1, functions become extensions ([e65f6a1](https://github.com/smarter-sh/smarter-python/commit/e65f6a1eb1cc9400e79950e7855ecf9153ac3bfc))

# [0.5.0](https://github.com/smarter-sh/smarter-python/compare/v0.4.2...v0.5.0) (2026-10-15)


### Features

* **llmclients:** add mcpclients, guardrails and tools to llmclient ([00abdd3](https://github.com/smarter-sh/smarter-python/commit/00abdd39d9ca999b3626e7d7d39e3499e1daeca9))

## [0.4.2](https://github.com/smarter-sh/smarter-python/compare/v0.4.1...v0.4.2) (2026-10-15)


### Bug Fixes

* **contracts:** sync with smarter v0.25.1 and regenerate sam models ([e066b03](https://github.com/smarter-sh/smarter-python/commit/e066b03e7ab491931bad66062448da341876c709))

## [0.4.1](https://github.com/smarter-sh/smarter-python/compare/v0.4.0...v0.4.1) (2026-10-13)


### Bug Fixes

* **ci:** remove commitlint's missing parser preset ([b707761](https://github.com/smarter-sh/smarter-python/commit/b7077616167098525def8b83769ac7c33f895baf))

# [0.4.0](https://github.com/smarter-sh/smarter-python/compare/v0.3.0...v0.4.0) (2026-10-13)


### Features

* **resources:** type orchestrators and vectorsearches ([68a1982](https://github.com/smarter-sh/smarter-python/commit/68a1982c8837daa73c78d7f51b009fe5a6d77e6c))

# [0.3.0](https://github.com/smarter-sh/smarter-python/compare/v0.2.4...v0.3.0) (2026-10-13)


### Features

* **resources:** read user profiles and plugin uses, type history rows ([6661783](https://github.com/smarter-sh/smarter-python/commit/66617835f4cdd0b26947b5cec4705346260bf019))

## [0.2.4](https://github.com/smarter-sh/smarter-python/compare/v0.2.3...v0.2.4) (2026-10-13)


### Bug Fixes

* **plugins:** return a plugin's manifest from Plugins.retrieve() ([b59becd](https://github.com/smarter-sh/smarter-python/commit/b59becdfa113217e6a0e7b2b1eaec7acef40173a))

## [0.2.3](https://github.com/smarter-sh/smarter-python/compare/v0.2.2...v0.2.3) (2026-10-13)


### Bug Fixes

* **models:** correct the LLMClient api key and custom domain models ([f174b32](https://github.com/smarter-sh/smarter-python/commit/f174b323688a6570dad76a9d16952cd98d49d2fb))

## [0.2.2](https://github.com/smarter-sh/smarter-python/compare/v0.2.1...v0.2.2) (2026-10-13)


### Bug Fixes

* **ci:** make the release tag and smarter/__version__.py match ([34fe7f5](https://github.com/smarter-sh/smarter-python/commit/34fe7f53f42251b68233ff3e626a7eb464abd342))

## [0.2.1](https://github.com/smarter-sh/smarter-python/compare/v0.2.0...v0.2.1) (2026-10-13)


### Bug Fixes

* **ci:** restore the test fixtures, remove dead legacy modules, and run make targets in the venv ([c9a8673](https://github.com/smarter-sh/smarter-python/commit/c9a8673091ea601d615e374f52c5c6d8a3948415))

# [0.2.0](https://github.com/smarter-sh/smarter-python/compare/v0.1.3...v0.2.0) (2026-10-13)


### Features

* **sdk:** cover the whole smarter api with typed models and skills ([44cf731](https://github.com/smarter-sh/smarter-python/commit/44cf73180474c48e5930b3db56cebeacb048987f))

## [0.1.3](https://github.com/smarter-sh/smarter-python/compare/v0.1.2...v0.1.3) (2025-04-02)


### Bug Fixes

* pydantic attribute types for chatbot model ([5b712fa](https://github.com/smarter-sh/smarter-python/commit/5b712fa4bb1d94fad49997d840489544eadd95d0))

## [0.1.2](https://github.com/smarter-sh/smarter-python/compare/v0.1.1...v0.1.2) (2025-03-28)


### Bug Fixes

* add a package-wide timeout for httpx requests ([979fa77](https://github.com/smarter-sh/smarter-python/commit/979fa77b38fa718f926014e9679666a068eb386c))

# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.1](https://github.com/smarter-sh/smarter-python/compare/v0.1.0...v0.1.1) (2025-03-26)

### Bug Fixes

- file and package omissions ([3291d56](https://github.com/smarter-sh/smarter-python/commit/3291d56897a27c39a8d860bfbf3363f7aa6fe1e0))

# [0.1.0](https://github.com/smarter-sh/smarter-python/compare/v0.0.1...v0.1.0) (2025-03-26)

### Features

- create addressing style chatbot = Smarter().resources.chatbots.get() ([1d1668e](https://github.com/smarter-sh/smarter-python/commit/1d1668ef2183e3c53ef57d9739ca1d5eca52456f))
