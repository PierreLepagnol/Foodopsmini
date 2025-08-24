from game_engine.io.data_loader import DataLoader


def main():
    loader = DataLoader()
    scenario = loader.load_scenario("data/scenario/base.yaml")
    print(scenario)


if __name__ == "__main__":
    main()
