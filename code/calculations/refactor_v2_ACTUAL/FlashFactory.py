from Flash import TwoPhaseFlash


class FlashFactory:
    @staticmethod
    def create_flash(flash_name):
        flash_mapping = {
            'TwoPhaseFlash':TwoPhaseFlash,
            'FourPhaseFlash':TwoPhaseFlash
        }
        if flash_name not in flash_mapping:
            raise ValueError(f'Unknown Flash: {flash_name}')
        return flash_mapping[flash_name]
    