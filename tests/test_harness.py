def test_the_repository_has_its_key_directories(repo):
    assert (repo / "core").is_dir()
    assert (repo / "theme").is_dir()
    assert (repo / "brand" / "tokens.yaml").is_file()
