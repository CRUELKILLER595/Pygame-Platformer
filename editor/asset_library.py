from game.systems.asset_manager import (
    Asset,
    AssetManager
)


# Shared manager used by the editor
asset_manager = AssetManager()

# Keep this name so existing editor code
# using Assets does not immediately break.
Assets = asset_manager.assets


def register_asset(asset):

    asset_manager.register_asset(
        asset
    )


def get_asset(asset_id):

    return asset_manager.get(
        asset_id
    )


def get_assets_by_category(category):

    return asset_manager.get_by_category(
        category
    )


def get_categories():

    return asset_manager.get_categories()


def load_assets():

    return asset_manager.load_all()
     
        

   


        