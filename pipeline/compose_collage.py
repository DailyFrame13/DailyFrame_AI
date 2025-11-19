from models.collage_diffusion import create_collage_composition

def run_collage(comp_path, PATHS):
    final = create_collage_composition(
        comp_path,
        debug_dir=PATHS["debug"]
    )
    return final