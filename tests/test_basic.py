def test_import():
    import wind_logger_csv
    assert hasattr(wind_logger_csv, "__version__")
