module.exports = {
  branches: ["main", "beta", "alpha"],
  dryRun: false,
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      {
        changelogFile: "CHANGELOG.md",
      },
    ],
    [
      // Write the release version into smarter/__version__.py before
      // @semantic-release/git commits it, so the tagged commit carries it.
      "@semantic-release/exec",
      {
        prepareCmd:
          "printf '# DO NOT EDIT.\\n# Managed via automated CI/CD in release.config.js and .github/workflows/semanticVersionBump.yml.\\n__version__ = \"%s\"\\n' '${nextRelease.version}' > smarter/__version__.py",
      },
    ],
    "@semantic-release/github",
    [
      "@semantic-release/git",
      {
        assets: [
          "CHANGELOG.md",
          "smarter/__version__.py",
          "package.json",
          "package-lock.json",
          "requirements/**/*",
        ],
        message:
          "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
  ],
};
