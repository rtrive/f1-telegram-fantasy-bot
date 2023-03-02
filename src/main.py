import os
import sys
import json
import uuid
import urllib.parse

import requests  # type: ignore

from apscheduler.schedulers.background import BackgroundScheduler

from bot.handlers import get_handlers
from bot.telegram_bot import Bot

from core.configuration import Configuration, validate_configuration
from dotenv import load_dotenv

from http_client import HTTPClient
from http_server import start as http_server_start
from logger import create_logger
from seleniumwire.undetected_chromedriver import (  # type: ignore
    ChromeOptions as uc_chrome_options,
)

from services.f1_fantasy_service import F1FantasyService
from uc_driver import ChromeDriver

LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(filename)s - %(funcName)s: %(message)s"

if __name__ == "__main__":
    load_dotenv()

    configuration = Configuration(env_variables=os.environ)
    errors = validate_configuration(configuration)
    log = create_logger(
        name=__name__, level=configuration.log.log_level, format=LOG_FORMAT
    )
    if errors:
        log.error(errors.message)
        sys.exit()
    log.info("Startup")

    log.info("Starting HTTP server")
    http_server_start(
        log=create_logger(
            name="http-server", level=configuration.log.log_level, format=LOG_FORMAT
        ),
        hostname=configuration.http_server.hostname,
        port=configuration.http_server.port,
    )

    reese84_url = "https://api.formula1.com/6657193977244c13?d=account.formula1.com"
    # Hardcoded payload
    reese84_payload = "{\"solution\":{\"interrogation\":{" \
                      "\"p\":\"G4qrOKfnpZPgORuO12oCbUYowJbu8hUrNyQwVkmo47rPiRoZtqeWF0yXru80jnvp" \
                      "/khsZxCCHsbhHChtrRaHl4ZiU31Pe5RtmGu0TjC4D3nyuQG9hq4MsJrkF4NRJX1xqwN15NMGJhOyR1GTxo6NwX5J2ExRELS" \
                      "/SoXK7XIFz2ocFBsrBtq9DQCcDU1e7+yB1OuuqNJCf0hyMYLhU0k6k" \
                      "+qPGsql6tpahv95IbWAy1vnQ1OXHom7RR5WtNfLhAh0Ctg0n2ALieXmrx0BwfLEQWCcGvYyTZjr" \
                      "/H9fykVu2r6eEcIhtT6UBdBVYFqfiuThZ778w6pZaGMfIDftpOFEGRlGjK9VHqBGyfeaW" \
                      "+gloqxV5sPAdsY9Mdc4Ox7O7N5RIEtSKc9Rb1cLUUASLSGPeBh7u3MJ0h0gBzx8fdA7Ppps0T48eKwAPvErcPunmFFW8z3irgxoHPAKM/Rirdk1inrA07UtJkVMDR15NRLNfsNEYHuBJsZpwLN0vyTUERY+OwvIf2JXYb989sl0c9fZbsnMhdBH8LV8x0h40o+7931VOLXUJ01v+z1IDO/PW7QP4ERPZcbyxR1cfi6pNVxt7Vbt+IVTBPGXRM1mX8gpmAW3HpNL/pKBp3yTATjcwlrnNVHI+5IMSopEMtyUUlaagPW2g08eCgwC5JeetWilvvUHUlhQxaLFd/g8OQ6KeD4c+ot4m1aor1qyYrWTHwtrXw40WGHG7XbQSqnZBb0Syl2eKkDLFwGBaIdt7udBZNuqQlvdOqGU6Uk/ZZ4Sfjr+fiKbRrx7m0z+SQBdXVKVcdV3M2vQdgMXbSIXdYujXmHGSNSRU5Cg9SW5i/DPuwnO9uiNSfcRt9DzCcjrrwpWGOs1jAKerUNNHjCm2z/5upMN6M3cg0lPcqwF+DqgDyOu4FPds9SMzb6RoFZra/4R/3sL6RU8nZBwfn8X1eRZDqIDw2y94V5Tb2438N8lABBbHjCXhp8nmNyq0N9Tw48VxEofMDuM/oZdDtzgNtJdEvgsoBh0pPz6wWF+GXEKFh+K4gfJ9GvMNXR54X9QgCIoVZ34uY9qY0hSqXCh9/jr8MtaMHW1wABlqXLvjOoY2NcbiW4BzJa6tFmGfDAD3bJeHAx1eie+eI19Yhc8vFMiyeL2+mWEzJ4+85ysNwWDfNko6IwVJI0pKxuhglmOi9EYQl5NrTI6lZe/fJiWHwodqQlLNfPmrRGS1TBgpMvUkpDrOfwIQioJE0qVvpIcV7Su7aacJJCwcUPSAFkw68ZbBTZv6Wnvm1qhYgTW6IYERmb7u7y5KIfG04w6NUjLuFhwpmDM0Dfhx4IaHK9QTKml/yMjUmcLfH0/ahZ3TJztoBO1J/rWVQhsCHGN97WksxESXu/++BgrBcPxAwM4LCznZu4D0vXIaXC/MqJZY+CgVkkJCSW0XblbXR7EELUE/x6CVG8t+PVVXJgMvkenLsSCaM+TIcfciAmULbzfAPOBcRtT3pZETUTb5hj4OJH6GKoW54ec7hJMEOQXzzG7ybjznG6xlf3S3oSRYrMtOyd6HVRi0F2JLkKW1tT3dv/ERzrtwxmuCfdLIPZUOsJEqvtkGgNg6tVrLoXNZsiKpj6pLTROHEcB6vgjXWh8jPJ4gIKb1JyP4AYWiOvCXlD5fooVS0sidze2Hp5Svykcw+q8yWx+7J3TK2KjHBuzhexdLJjwoBVXdXUDPtyajocvzFXc5D4EWZKvyUpxF3sObnyqGB2PqZ9trO9YwWQtmjcTLgfHK/0AocLJ+1ew8h7qE3oeU2ckiA9M12KpYijoPHZWp9sODC7YwHVeGmRMEpl7Pz+HpQmE242x78AT4Xz/tPjQ63WY28hL6k/AOqytk2vUukemhV7To3tFbqEF5XAEGfl4yQbmQMb+46j6aauxUFOuu96qoYsPsERw95Zo4egMFiOzS6t8J3CrnvmjqYBnjfSFnXSHpeNcy3YWSDEEWMISYapsZ5Oax29eF7/o22sCV7UQbdhiYBFW9qPFN9pBBE2pxcfQvMYG5+2AC/ELTIpBWh1ds4KkqGtwmsSkUH7UTsZdIr517vV0XWdRG5BxgPXx0ypB+Fg8QkYK2ccQAdXY7reIJBZZKPjG9taF5dYZBxd8I77zHVM82eBEPDy9Vu4+SpyN9vETw2pjocuXfalmDWjDpNnumindfY5e+PJhvP8hYO8HanP3WWcx/GaJzYazcc7pWU/n05FJwtg7bHFmE5CJJuaPy2AsrEx/AJTta9THzZ/QnCcX2bgU0M3nDAB7VDtyEE6Q9/HZjRYt7qiTVmNr6wJDYxubJmq6uEUQBrkShLQAmhMl7s7eR1UzI823iC7mL9vpAH9bQvjbZg1at95PxyTi/nI+OOOPIb/UOCUquzXtTJ5P6ArPgdVwMkdG7EZbEAyvutHA2YNFeCyIs/LgWwSkhF6NJRYawUSqZ06WR1JKlkTjoAaQtb8EFXqq87e3zkPf44GZupf7+v4IgvneHL+2D6+lq63L5XzgqVXEPp/TvVeXsx+Q92kmJtO0dsBfSrTT+R6lribMMWOXCJRREQeVrqfHxvCAo8worxWPhZYsk0iiKWjVPOo9xdn9w/kv3NDKxz/SYG/4hnhu1nMcXx7TExLZSaThYxgtc8uIizV2zceESJznvggH5D3gdbu+sjFkDIOY59YLi8vXZf9JdRnkjHgm+VGckXuDLtVqtmWmUU0+M+M+670we6xXmuBiSXaExmHTjg9BzO0AAW4fKvq2sKnqR3VGAesKOhuv8vyTeWZ4nFjbrM48ksWzRESgRNRkLKMaszNliKumvMieooo4HagzuVkI1m/pXP9/y5tD0+kelQyedAzH0CwA5PJu4DwoZb27jVz9oeJB0clEyWehSpcPz/zao44+932FzvFc3Jqz5tCtkT12zt95lit7uxAgKsV9SXQpP/pOIhAy5xuhdxBb6WgVIMPnkkvkIYkkXdT3rt8uZKByFHanRCBDY9TRviPaWNIzzphqHrYKO0BPMwlUcKvuv3LpfoueSISJWRHAn6qwbyrSpACrQuw/MdHLpcGZBHuFptDEm5wqBzWSbTMSaiHyCk++R+ysqJ4IZl+O3VdsiEiO9yK7UYreH3MZHcjmoID+jf0fea4TCfs9iovwONH5D+PSmDI/akupn4ibXYFgFBoIA1exsfMUEoiUHphpdBmKcSX/aMnXSR08bdEG1b3xQXrmjvv8xc1r/kf+6r/qHdPnWFYgUt5FMk+SBRlii8gWnCz1WHqapEm4pf8lKMM4PUa12cv+J42zCD0knHVdo6y2eczZ0QIqUuBHFLPieQVHRko9/zyVlrD0iKkpAjn96y88I11NvlVirvcQrdKNcwum2Lmbero4Zs0Rx/dcehaE185aPH9Mg2l3FHXs6qckHN/TE8sjbeRRED/qrjnEkXVvRer5rKvzkd3x/uDloSMoeYh7wQUhmIW/3YhJUX8+WKrHo2ZMNse+s34UkMyy+Ict6S6MOUU49ZwxhkqOnS1zuJnY+axDjlvJ55AM9mH3Er5j4cWPGznjsWfgcZQ50Hsn3n84sEpAOYo+lg5SlmB6ppfifn/p49kbbpgH2gR5uzK2WyURPruOqAOcJd1HTyxHTdEFAVtUcDQt8AbJysiL2pjLS7sAntgwXS58oDEznf90L6sZ4CTtj2Cp3B+jSS2U9MadYC/6111k9yB0e6pXkIH2gc+yf3yF6uDWL1mRKmIpRncmRr39DVR08upH+2zAgr/tv6E3mQTgIruObEwlcufjd2khsvxat4p2QiO0wmAeTIrtx9mb2jxbf3+XAr4bUvrr40sGJvq/hvuu9c0BxbFbZnjRWSz4R9uPL++j/eMMzxXcfjlKBNRbR+su15q/+ojFGNjPIrZGusE35OrbMDau1IQNXrqQ5/+9izW5yopsAZkYMCY+Q2SaZ/Z2FmhLIst6OSmIX/VSuwk1Is1BWpk+EctsLY/vnEfvJ5nS6HmUGcd2+A46f3gZtGZNxqcQdwQeO0aIL/PAZC/2f2ufyYx1o0qNhZRyNBJaPW60XWJHcuoyUH7yENa5jryH2Rqdlji/qnAnSYuXiWtlcN3u+HS80xaUtsiEFUMxzQiixcxzaC49QSDsSHho4FmthFPXxJSRal9qJMGmSUMIubNd6Arm9BvqYTvLhtetlnf1aipUMLnDIMnisPOSTSeDy0QGYU8Eyr2113twYG9pSiOf4ezVpQgw+4KiCQGN3PsG41CC7ltEaGDpGKGHdnIQw3/Q6LMpfAteMosezCjuElz8fDaX/3Hrg5Rmx+GpRtMRLgNMoiZsnotxCDWaG3Pk5Mm1yRtUuVwdEsGif6u2gXVN9HMNeVVIQ7TCO1K3ZEo7hu/2jLu7/oxiODkqHO/BLSJb2crGIaeWwt5ytOwQJvuGm3aCVEDTfaOzBioasMLeqid+N59BwnA3i97a4gpw87LTKG7gZKkbeL2+9nAVlUpk6Z33cuBY/CLQWcBoPkrhpa3TCqPL96tqBGhhKEzy9ZYoJ0wt39QseeMF/uTFIJ4SwPkA69zcY8M/B5YdQxzp0oFRNV9NK+MSc3MbLg80QAXRTVARs18tti8iC21TecAXAaR7rSZcBIcKUbtcN5PJxgACk32b+FEEDMgBfKcgr4U+zW7C5KheHkBgLXxSCmTiMf1ral2YG9A1rpx92wrgMAhaFCLoSWl/e5Fz2doLVZiHdsXdysRo1KhfhG0c26Gj+DFQTbL2WHss1Wd5Z4z9XOsa93UuX6HTkylLDDb+PSxE31D/zrNBCti9ZcA3A/QztXyuPdQgvqjjt1XQAnP61178envfh9dGdYoxV7bicjOEzbW7/ltsa3lpkKaqkU/okMoodlwO/9j0HuJLbXPwPjg27vkNjUSMglC+IIPXc218Uw4uKCKxyxL0cu/wW7ByhhqmMGmYSi3PCeJWjN8/ZOWjMjvfEr7+42UDSqczBjvjKGW6WZQLrhbQGXsnKyC3cLptH3ysUQUPMSx7d7e+MQ6WXO2/IpeX0wWW4cD1iDjC0afnVNZhjdjnG5j/2RMLe+ZFxw3J9n0kbgzi/kLM+eZSj9OyhjMPIPx6tHDRQ2vloFLW7sq5mPPq/iMgMKdShxFp0l8JpaoJR2tjypNwMqojuXnf6wFAXUl+vqwzH2l7cwa4u5IxtLfQ9egq6rMhxWgPTCv24qMqMr2UWbA5CLIttyNxltfjwmFlVhwPfHeT4DrR+VLiPGRzrDtV9HZCCPq8puQdBxIN2jH1xpGdhYVMVTmLnSUgohm0sPQwr4kN4Wpxm7zhrgqaNg4Z4qM0dA0HdiHeLc8LOHc/2QNUqePqwmytpYoj9KmADmOvFJJPgaljYOB/MCio/DPOo6cGGXAU2zlA3uTXHuukLH5FlFwQRfuxq1qkqAZ5z5Ha3dCyMa1nSnQkTWXLpdgFCNXc4ov6ftmsaTjweWJbv7hVck17znq6qGiNX3PI4o18bBrzzc6oH+DqvNM7Yw+e+XcEsADXvjDQ9Y4DD/8bUfmn5zZ4HnpwY0gMa088MIXIt3rLQIDCFnk0ChC+jLmO8WUDe7yBw3FIN6uEW1VabV+/OeoVhbWDMnKzMKAQcsiJSnIzFSKDOcB6TjjkLuwotWPGJ2JI9awlKJlboTOQdcX+V6egdrCK4HjzesS6SPyjDFZhpcVPXXbFukq8Kv3mQ44ax7+NoTg3N4owkX/LyqX87QebvcjrvbrhAOdDPVtqXBVsxD/5BD28obndN9SfZnPX0T+yIZgMKoMuQ5U96rp8S2xhrJMvYIPoJ7vF5HGcKD8IECAyhthJeidI8uI3pNXu1Oe51wRjlsuBOTjJO75icT4UBDOBPvIchS4j4tmu+nBuo+f6JUnkAxuA2t4TUNST7EAQJjBQNue69JkU0SLl1hwyXb3l9xIgTT9YCyLIDWrWnetU5Z4G7CgBzH5JcR6NM6s09f6IiBHPkn65aTQlSi4/qw0brjXLOVr9T0F6kMgsBAPdoXoxGRpCbJZTLHOYxlvdyJv06tEB5XT+uO7l+0GV8J5pu1WDKOqnnWvauR/jjzjigxYfKrlu6C88fMA/uU2FAv3msrKgFd2CL2DVk6rftepBngpnvIB3/Os6Wx7SO8oMbEXf5I/VqqIlxubm1kqcp84foW1NXHwEANBJQM4DD/Do/04le4zArjM5H5Y0RbUwE0oyo7qKIqBPZwGChMO66qpS1+PuUY8LbeI9bkYotKyhhi1HjK/obWuzWO1kW9YMg8pGRXloPIMEgcSu/G5d9TFZa2pl8Ml9OIzDtebreXRuSKuZ+P2q/foqEHV2ZKXkAmMZzexmejD4X5Y9MbPx3sd4+BdI2bjrMZ5uMl7Aue214wX4Uf0rnaR+0aYQOvMbDxyCVyUZqwTrieTFPpLIEwnv/I4kqsszcgcYGsq5cqnJ/QRs4WUAI9fQO/yDid2s4nlmpvx1go/GKhJlNx8hNSWwlNKvqD8T1uGXHxUJjwkPFRTFV1TMviVjfIdTgZVYuV5M6+rrQXYkOe+47Vref4eiZDkxBJ/6YE8h15Y7hnbp1mtmO5fXZdH0ETE9pynhMe4sn22OjstfJAEKlnM+OU2albCSvtYkbGyv5vWTcSf8iAP2MkUnpk6VJxvXBGU5+Br/6VKw+58HQGL67Yr1vRyxttzO57qkxKA0/emmK9i1ArDshKbI2DqQ8GOFN8v49S+bxim8uQJONKy7XdBMcLj2vA/urX3YfFnFCKlnBSGNtqq66Z6g9vNbkEiU3pQN9kXPE3LJE6ASn/Ct74cW7e3/3T/pdlLutFx3jTBvFVSYTmXBBcH9QVg1PvLZtQ1XjdXLJrutwCJ+h0moddrI03ZBRL/9wJk9od+4LKQVD2aJ9WBQ/AWzoVeMNepqv16dDEFpcdZ0otYjaJ1l5tlebzSVq1nvtzoJpd1HAgEKfKrH/t/hFi0GHeETPFCsotTOAC4H/Tal2+A4suaEeUKaZLRnH9gc3UJim8mp2qux5OouCI8/mnM/hm2yT+RhirsFx6lSml+beyzzsD8rzM9P6CJfXPSVyHDogMFkl/NkzW6jJ6tgi7fN3Icb4kW85rhilOfrmd3Wll93kcY+l0lWgDwuBOdvHB11dqskXkUyiDOtYQAQ8yUJXP7zqQ3gfI52Mrjv8JNHR/R3S3TNRGAGPvy05SS/UasGjax/cL1EFV9SNQ1TfZ/inVzbQIOwIa3xNGrN/vzGQ3vw1lTxAMpvVIqx4ZTvVheZybSpqNgdJCaWOjAdaBqtOhHzbpbn25x/QnCW4lNVqTaq7ly6ArLiPT9AAJne+6KI3PMjEKVzA/9685qIEIbRTuCFsCR/ZhXutejZXb5xfj0jNheK9M9LP8qdVYcHLVyqZzD+ANPmZFg1bflVgbTUeHLko/Oe95E6hQeT6e6pR8+SGyN5CYJ5akLyEHxg99ZRqBnTK1LYjDaWxcckKbIbXGnTz6Xya8DeTFRYvTBE2c3TY6+ez0AxS81DLbfWBRtoa2kPvhCeloHwvogtfSXm/DsKcl08mg1F/M0EkcjhEWDArumrN/NqDc4vhMUCR0rro4UafVouiwAgXCfZt/4PDZjmbu8Vc+dAVAmbxz+MjS1/N/Cpran/jY7unvuenG4ONPNQ2gxckcTutfBsb1wcf7SH5yAtLb6W5WxlupK9gY5TkVjTVzMX9PIz/z/1xCE5tO/v7/YL83zigvMFsX/5CZsgkc7yDyPril3ae8pqrioYrlFbqQxofZdgsE9wwD0BzdGHLSaC+cp3OcR1g24iiEqAWg40ZeL75lXlb7YNBRonaK8beQchG0x+4kvd2fyq+YXoS4N/i7AiR21FtFYL9sB4LKw10gfimFCUtA31Al3b+sOnLxaW9S4Bq38aB+l4/Pqswe/0fj2Al7q8axiqYkJOfx06KIGfDysMiLMp2l2Hl/PNzY0ToCP0J5GoZGcgVd6gW1cwgMl8p6IyEyj7qwVWFcfh+4i4uQ8JPmD2K5cPLb2Qtj1wUajt8/C3/8o7xoIATHntW2y8LZH0bvDQye4r5jiuaVMQcIwGPJQOh9qWhIihKbOOaqgc8sMj07mmSgmv19oPEqbUtPnaogyv9/EODsMBdxsOf0nQTIpJbnM1YY9LPDiqS59lxyZGHoNYSJAsJ+cbUKuNuAOBcuuQmzPiO9MMvVpdamVI9Sl757MJWQtQcQqWdt+vS2LYSE+a3e5+80fwjMMJY1FpNge/ME40J7E7ZWnuJbuW1fW/rFvSmhSf+VhzZP+0hil2GIa4gxTDsUOm3u+5AEJU/GWfn+BCZyNnb1WXdSFLkmjl0zK6p4X1PBs8Be7EAytXwdgBsHKi1iCpWFX80vTktAaPXVAhVd3YTZCK2OmIYC+v4w8TaEsL8qjfjWl7ZWQ1XlbUlIjBshQmmb2sIXmhl8o/jXv32VFUYWP+CI2rWR1lmg+inYRJWnZRWoZL8l2wMxu6RXy59VTIq4VVp7DoMOtvaB4c3EsU9fIEX2OpC175irf7zTYQpT8tEpG1XtmctHZF2XAxCj4IMYSdaACIJVALsOuHmveNtZoQKXQgE6XYbWIz2sP3SJ3ov6Jeyb1Ne4qE7nXMAxb5TZr4Zw50j8npwTIIeYoc138I/oagt3sN4ffISXe9AOV/J+LKlkoAhSQqrsqLLpFgiSiabvh2WF354YaMftbVkpA/AAIGNBer8O01UGgt/8sAYvUr1Y71Q5Jcs45JgPaESMgBGtkPFh3667FfKV5RVPRJVB9VAiJHV1TGCTUG1k5e/lgLFgI2TKE3QrgN/lcfBJkxbL5qL5ugqnwz0lfd1DpNZbAgFZYgo/IDom+s+ZthPmAAABRaZhL+VPx3QEC1PP50tMgWikHzZhgOBwj/UAQ/c852398PNqj7A+bJ48Vn6d9HtWUQp8zPnlYfO+XiSGYg9GYACqWyRYpboH5IMvW5xH4cOFyHG1ZS/Tzzi58tC7WSAu42cNsa5mz3Cfwf0NG15A7jUmaUpiqlfVHbr8xZT7UKGfyUJ2ntnpGirXU6FgcNycHe8F2h4olpYzEb7eG2Jd06LQe/WnE32rcHln6psUmVcZKGKU0vQG9mMHD/6HrfGsKuSvZw8WS1fQDVSnvee9N/qOIzd/63cwDCMo6E2CoJBo5fTmetQDXASPs0sSfrHwQFfhKrfvQNfAXSKUhHalYERYudSyzbQIC3V7XyiCz71pCU1mSFluzkIf4R07mEVKPv5BM8Xe4T/UHxgxJlCUTjokSo7pBvvOyE5Bp1I91SqUv0fmPrqDzCva3i9LHC+hQ2JY1bkDUyrDxn3ZtrEVoO74smOvwKr0zW8nVsKnNpsL0JbkEvHXCU350up7j5ud9y7v0mqm9aOWS1nLpeMcyqTohGPcMZuy9syLOVk1dWWBkYJgL2z1nerGCYNjxF7mdPp25Ecr3w5d18L3FDmV2IrfjV5f84NXSNrjgSoE/AhdxKut1mpFtG1d7lqQbKPldTl/w0GgYwYCO9B4ACZHUi8gMLj6CrqW30oPc7rov8L2bNF49Ln+txXpM5Q0q7g0uE3Oplbgcdr1It/6/Wc4DPEBEt3ztXEeKZsXefsyFpjrel26qwHrB6S3ASQnvRjfQwPPnEyarcM/rBPn69NihH8P82CzgNvUjYtBvmVS/+25F+SDnf18SaCtGv4YkiFGnFnidvwHO5kUvi9q8KNPJEdKinkksPbls9U0Egch4vWv+kpEfbOoGmBg18QSLnhpnBqWo3B5TAkm8UbePRMykiRj2mV7513s7sayLTdL1LE5H/CgxLcTLZD7J/Mn2TZNJGvh3MRE4Eoe9ZaM45ykXNIK2wWcqOHvfjvTT8CNWyUurGCTdAytBqKiqk8xOJR9X2M6Qu3Zyyx2Eydr5snCvgvIuX/jPKnvXvjb3nGMVUeAJgZVwDjXm4TmO5m6ycPoiNJTmy7F3bK5YINJ9SXvBxvv96Kxhr1/ljWuOrVM6ksVSXFElgXEBu1Y9zFAsKuKkU9r3qjYn7lEE33rGdUF3tf6gWUHsRTiebDp4k80YPhsjh4SFDv6f2YhSzbh32lpx2bKu5gXpCNSteJ+OnospmlQvQtQNbWu6SmHYnDCEnUlazfSe/25VntIoS0Cxs8XBaK1D0atpp0p67kTDkw0ujfxVrf3lkiWcMsyzKFVneRAIHkbUgNC+8xBcJUwY5bMlSbV6czAHOjd6do+lQ3gPF2Y7bukf+0rhjz0XzGs6u5GqH4Fiq+mqbjFNafPkAqEVjPIMn70LyOtbVmNm8T9KSFWHC1syiz/4Z0GY63o5hzeAaZDnGEJwCJiaRw8ytpdh94pvVpl/1t60YlTQ8TCIUHo0AQbZGYJngpFFYdLzxhH8WJL8ZBbtpIRge+dXfGu1qLRSds9uDs5Y99Z37PvdTEZZDIGdA7pS85hkAlumyJAv3c4VvEpZB1LZ7MEpbF4soyf/R3UAi83YTLXF/k5Eac/6V/OimQwErXt//1eik1NoSBll9FtnnXzZfpYUiCjfMbbZPI5W8+5FXkDElpMaBbqtHXGeL1YTYknCGcsY36rxTn6dmI4ABHX2oZkYP4m/cys6TIevadw+YrOd+kpJYBl5AFqyQDuSn0m99kXRuM9v5dMPX+J3kkAYpj/1h24bQZj40Qy9VZX+Gq8v9lS1v1O+CPEMenVwpO2XlRU7EmRtsHpICpNZ1jGZviJ+degIvUa+cwxi0K82pFyZiJYWxbQlfiqVHszrK4FsOAN2mJOeQYVNkum3UfrxJ7DTfmfBLMSdFkCMqW23qye3o1M9+LG/dw4vODnqI31SdSgx86R/fYlXRdEgVyxij3VTIrv0bI2iY1pmImyengufMvJTy+eNt6qzRVb7oEuWN9NyOlSeGgwnAZsSy2GfXhWuq/2YSBbjyDqgDKuzsqh79l2fYdGnrP5ZxGCCSr+Ctopa/28BMqnPvwusJjhiMbxqqf4xDzbPfqsZQ69Xz4T76V3Lg7lMJslVqZGHJWDTKX+TeTSAmGPuSs3dZjtPRRIvvi0wUtTXydc+a1wIPPfiKs7JHgIHjOt4aVXTn0lBL61+I72/mNK8G2hLkfQUlH5Iu6Jdodu9qmd1iJTT3qSfxyi8EqPg+eG4ZOMGmr4CtNAAIKrJ9e3ncxZGxPgYY8Sa9tbQUlr69GTncHpYQVclXzU8Y6JLt2q3DleotAasIl0gUpXGNFJha8o4IwZpInUa1ICKagk5Ix9d14xcAWIiymBb60YZEgtAO9hjdUtQ4wtP5uvpGjBWdu54UgJrOm/fujURqwcUJvnF5vEAGI5Z5Cwt4Tet9Pxwc+wfufDkE+QICc7bR+D+zK/gxIYbwzppbXORPJkWIKBIEEL6bujPLOqVAm5tjYZ5xeQ5dZQQ2bcez0hDoLYqQKZ7qWm6gm5CgCA/FpjSZb/YJTMrMkM/FGkWdgumb/Kp0OyWvMQJoTXzTT0GMVPmutKhJdEqCzWdLiDrzv2PwH97Gc1cyYoK8quft7fIBIIwEUehvitLcbtWcCYC//mtaNgSrpdSYEJJIbwM8ESyoycoOD6O+X4csfkz+CSC+CK/sX1JwQqV4lZnAajLog9a5u4FIqVewuPjTV5STQAIgAthXEwiZcikKrohNrHXcVWOki3/GuK08ZedXbAvduraKQd6DRnhUhjYx1ez7JICp+Hk4A8EgU76eK0IDIhVX3VWH/JquhucJMB+19k0OR18OsQ9l0u5PobuccjnB8cSpGZVLO4RktZoxPmiouZASbzF31w8gPgXlu5ZtYdSGF4RxIaQJeHus7QuDjBV8Asm/k5T8uZqlrpGt635GL4FJ/wofqYipmosUFw1/Poqn/nwrMLyqxUdJsI3QgfBBlHD0dkB32IprjA2x8kM56Pbskeg6ylLX1olRyRiBXswAzIzfUQmblEzzZ41twD80tWdzizJYYJ1usWx21TAk4dq5LmulmPZSB4J4pR0X+2bBCFhyOcaK0izNTeIAF0YiDpdtZFAffFoBpQvg2O+s+ojgZ8lkp8ZpXHk12Bpmm8gjC8s5siyGsgCp2jK5bCaF7fWoNA3g/nEI5mlSO4ZXhO/90+nJawqlkZeAJgTGICglEkBZSt2nalcLtIZWvh/kyuCU1LpDz2WWc9L0DhIAIeqzUxAH5v42qcc+elesrFMzWOWQp9ODjiM/YxfYXMJ+TMOppSpFcJ7e09Dl8bw1lLZVGE+xTUq3BZfca9vhw+sn+0fBNwxTdd8vRr5QktLcvP6/dpjRd6kCrtNi3u+0JCDMqrgkT4Tx8sCMsgSvtrFgIK8cAwpzXV2tboZIflcuAstrOBueG+Iyr3gWTcwdXuAqSOw6SfmcxDapULijxVOnTcJwvB9nVSZEqldTlr9ZfVgmLkrGJ5riKguAdh2tkL5OxWjN+95TSlpOdQLXOgoNPpR/Q3L6O4TlosTE/AOamh6Szkp2XOSG13s4U8WaxwT//SeGxvzCXygakwfN3IQoXGxIAVbvHBNkoF29mXjj4LmQEmkWaLK9NGodqL5u4Wz7/EW3MzipuZbX7i7jewxTNa+7NrHwsOO9QGTh0hl8IUYy1pTwujRcG3hDbVaSuu3v3C41o66cRkLOnNg3sHj37klbU1vVTqzcTBVbtBKPgYNXUXVVYI0t6AusKya1WFmh9XLo6bxnl8DkWLA6SiEO7BoQpqJ6IR3RLAzPj8PG2mxE8HZoAtCrZsrjhzVawmBrYjF5WfWjBmvwRDdR97GdicaZ9v9waHNvLI7CbVQojt2FVeqwjfdfpPMJN+/VlS3KBQuGL9SZMWoBk9rbgwxhWMl8kT9UwNWw/0Nwo4yTaBKzB9ZUC5fF5BQD7yV+oryjLO8C8wq8VNxccVGFl/y7FuGdhJRbFyM2H3O6j9VISyUG4PMeXbIus46tdslEm6Ypiba1B/hoBcEgMTDJ+oxkMQoqPJ0PK3xmRTQZQRK3bXtUqkYspAACMkYUDLETfbIw608vVOhBPMlfOKywx0dS7A32jRd0Zqx9D9VFxNR/wCONsLpfCiR0Q1YmCEKoLvY0dB+cYulp/+clq3y2UXQ2bAurQSJmJ5sj7JFWNdrjAuLX0aRVlJIa0yFxsJbO5lFiLrbLFBt76wMcNIa1Q9tbkThkce/ixD5mAhm1EnkOzyGPyeNQdcTsPY5yCc8er2e9Iqlj5O6VyVjLNF3dkUGwFgbOuqQfOP9TNNGkOXn7i6bkxwwBNDYQ0cLZxn6Nhr4WX2kex+bRAbBsd37ZEXYtx8sk6ge753qDQoCUaixfLA8jUjjkzGDuYPjvd9dn5R7xahvoeF3SJ4AIoIcnJPvROSe/E+rFoWhZf6YNWG2VXQDdAd8okCu2aFVfeVWYI+5qYX/hAUt7RkRqIMPpWETSJKaTTpH07iv6gfLhvQLJ4K7AV6lb/cijUL6N3Hg6JORGzWy612hgCiuax0f03tlM6sTzh1QgQZZtkkXVf2/t7UyNxOqolu/0oipMCf9X+DU9oSJC0cRaTW529dhPcZAh2xr8nkIVCRJAk7Mgc28bNSr6yO5l9srUnLd/h/JPpx4gI1y+j45HOYGYUdIWcrQGwTo7v5ra83ctWk0sQyvKxHOn3AHvDVVn3HJk0Qw2TOnZ2LJbaH1cx3XLt6e/5poLYl+8il836DOj3r5Z1/ZPgkFh//yY/lnOPzZ3+/pkEG0OCEalaOYpP0B81j5b7v6ejGvn3KV68P/2FV2oHMAS+vMmWKVFYwz/8ybExIZ8JxYOw31y5OfVALSlX0xohh4hMOHKk0GikRdf3eXGpPTBK9x5fhFmES+K1ZBEapi/18zMVPKmPAHDSVcvqI9Fc0QOhgHj1ie6FH6Z7JJhfTrp4cG3T+bph7hdVg22zAQj0GGKh2itttJLRIo5J9WjxR9PWgITGEYBQw5AV6/Y+SuAXcb2ClA7KhC9na/ZoGwrH9negy4QLv2VFW8yYi+xK7JQjpmMMmmEJvQsPcb8fgcYYW6EXOQZeB7MA9RPmjnjZmwps+Nmb748gXCzKJKiF/raF7LQ2FTZRbSjHdHMMA4H+blvYSeawQ6LNdWiN8o/sf7EoXElWY8T/X26y+LJt2OHyJubuvTkFL9ff3M4XT1eqzKYIErTqoKuUZvAeiud+mHSGpw1UIF8fuoy6rhjF2szt6l8Qf/ZbbPayh7EEGM7TXsXueFlRll2j8JRmNu6+uWL8QlyouP9YWb3eb1NEx08Hi3HMfdcxzlswtuOvxEqqaaARUm0P1aD+MMGO/j49hEAT2sfUJTur5V7kwGToX1fccC/3FphLEE3cQ7sagCU6e5XqaAO+TwoxAoKNB3fJL1t1POr6hCApQeIHFEIbmZR1n1eq33dP3akIgt7yt90VgCZwTlLU2Y+FPdwT0CYv3+N177Y9Ow16nmqnYGckHnJiaEHqTOGA7uP0VnE0Duag0jZpzVTF/dGtQk5WZc3gleTFe/ku8LYFbbYSCDi7//m/t8OonFDw7Fv/68TK2G0ceBldDjgw4Pv2KBhzeak1i6k1NJvnTNxFXVKPM91euRiGZGBrS1VCPD4kV01ArNDQfMMRiVF45S1CvZSdU2yy6ja8d4e8+eIEoQeOp5fWT881b+SzkAL67K3OjPfQdddeMscl/kZWSlHS5Vp87X6kx0El0daCUY5zuZzN7nSkYLsGkgrHt383e+s3tEyGj1jEpf/G0M6/JILagLvZd9FZc3+z9VH4RF6863hIZg7YwK42YbJoiOVVYYB2qt1yoA4OtQtckL6GkpL3hyKs6DWb7iNI0HFpNpT67R7PVQ9EMuFaJTK9zd1i2VoIYPlJ/zQ6qLUgDZi4fQfzMz/JlYACAAHBDb1gJzAr0gMo/f+KRNg6Bh3NzGIZnSCgVJDMosWnsd7mmdKiMHYQGQjMNDXgH7xZLDiU2s4dNn8Ogcog4l1lCfb52c3FrugG5yIKW471jD9V6xCwSHDpJtFbm078GFPESiKkZGJrLkxAinwv43ROQ/5oSWnKx0Dz3zBNCj7OE0hzGaUpkCUnYFzdTLEhZzzjmWI+OCf8eWRj8UpqdSTEOWMDLbloLjtzn62qDjef6exuDCF1BDO9hcgfN2ed/w9T5HE41yx2jrvKl78HvYbXkDlz8rllrba3P4o3WPj6uMBtXWPHDbHK/dYu7nGofBYhrv7t0P7A3euzgAG0UAAbCTZHWzbV7esdg17NODT+m1V4pf1I6evvgcYyHzZJvKJshEKMNLrrrAGs+PiX8lgOBKpsQsknW38wjPfeIhN83GzPV4aX+UzkZxWeJFvzuJtaXyt+mXgtgwgmO1TMgQTQrX05NTfEBQOF658cVirpdnJcX9ajGXo7uxcsbyQG1fUUqFrUJlInVIis7SIgd3xmqNcWsVG0CAAjDmjKuxu/rUW2pJFsUOgGRGRuFNJo6YnrGRdZfru0naFp49fjcwBry3EGbJjjIqe4JZ++ROcla0cqLP0stqQshpN7cVDjTQ58zRtf6FpJw19bLkvS3xqqmGLGwlX+zE2LvzwrDraCY0sMM7igY0QJMIHAHmiYjxqKuedwwWNeKMBmqYdWvQ6cmAbECpAWpXAsFnuQq3/F9zfTme5zL//G2ux4EDZIuB7UYPI0sOeB2eSiOLXqrABTD38LWJaAn/McnGyDO7wrctSKXid1UwusW3P0jGcTI3KO3R/RPvk6JG4l7dPduJGIMJGreLGVpODfLfP3g1RcwHW0cjHKOEKb0cfJC/FzrRHd9/jeswSG0vbIlCKHa33IGgGRehF/d/RIX6KzZH8jNpkxFbwo43qFNaYURUTEZByIW+iQjBNm80I60m8bwO8rEC6g+0zGuIeIEyUz/3HLrGqABMz1lhht5KcW4nEgBcISuRDLOODVVJObh4J/CmXtJv3kZEjRnPQri5+JA1x22ovibkC99eubEuUgrzbRscDGcd7151wETyt3OZGHUUEuWFCOUPY0o51bPLxM+tCc41CRCqLunj97EkNdr7V4YGanOn+1NGNjkUODshKtCos9e/YuN4xeRY4AaGO+0Q1PYGIyWlqvZnPj9tOw1yASksO9Pda+g6I20syoOfPvNwY3ULJxtFTtEuVG5RSssWhBm7LgFH0eLxOvQBGiQtuzSceU/102kwB3XEUgt7PC0Dzo8ggDvhguB1ovSaXSQ1lbN3k1mKOT+giZzswbs89G2F/Fi9JjnL6/NiU0ozASbR5wLljOzUXnBk7kOMjU/xRglqIyCPp+nXaAmDdlo3KR1OXr2cr7GcYHdYaw5CQoYmhPGPa5ZfeUwGSW3Nidx8LN5W9PDhOjcgUuV7ToYnLus1jzWGdZ8/lDAB+FYm1NR0Rw+MDkKA1F1C+02YoCOOurvaL7AltEHzlFeoieZmj/nM6DMigj5jHtpB4g8RYP3uSOG7fBMHqHsuCy5MLkTypSHczaaoqJ4JHtsrZj8OITLeaA4YggasGhbLzcm34ve5+Of/2n5jzxXjIw5c9N8c0TwR9JCSOA+Q/Yn0iSKYjIXW/Upp19iFGNoJuFosdJckXXPqP0DKNVubBqDbSLLgM+0kRJSFIqwJkwJoaJjBKO3f7D5/PChzXc2jCxsBI7UP/iNAHVnFtJByrLEsaV4A1Qn69PMfDif+MuWXi3Wvglj9uMuvA2WEter3A7UuwuQrijpS2XHEeyFaXjM9EGT4bQSTwX35lylWv83S639iQXFxYU8Habjk91qEb7nvR83b7DQLdvLO2y2yzEVIyauCeVv2OiLukDUyMnVxhQQs4uPy5lwNNXUZXYD+n3Mr00xE4/uWxS03ss7w/wVWS6yRZP2+0Re7sBhhstB2wsZBiQWAZKdI3sS2QfDf3aQ2Ohlm73N1e/9OxTrUFGjJW4T9vn6dpJT/lRym344jp4Rd7rU0DJdq0F43rxBoPvSZzJyBVMJTEe02NX1MJluHZmZanrK8VL3E5GPL5J2pGstObO4Ws5rgdnoIyU+DwhAqyIUPcfsmNCCYEopnOihFRfMUm4l97hOrszwsq6PagdgurEuooE4jcjw9s0UBD06LHGNh8pwqYJeQEaVi/nZ7VCLeC0+wUPAsFAQOl4McXKHZ8woIWAs5g8+/MI5Mzwdwb+4+XMZI3VoRnUGn6kI8BJFsgUr5nCXEIcWMlKTfYWCRh4XdIwHN9TxtiSe0VJ+4ttX18PIgoXsJxLIj1pwRNtyKIiXhkLZp6NtgD6aR55RaImN10XwxgSH1VMAuPMo1kI3jDA8o1uqh/wUDOWQx0GnL1GXY8W+tBqPcDAqHKaLCCl7EWoOg4wjdDiKHt+iBlR4fzDGJf0h1AAcneG+ov1lIsYZjsgzMGUHKvT0lU+mzf9etsdMjFbahaKZoRp0u+Gp4mqvLW8T7MUHCCjwiGZxukmPduavgwLePvBRebx+/MvxV8b0tIi9z803CKmNdHO1U595n+eP9ub0ObPCFAos06yFTHpz2sHJDlXntebSELRxPhjGWzceveBOY+8UXDUBjGfBj3PcVls/QEaOqCFxuHbZm3xRAMebM9SEHdUxD8C/5Y5Wi3Ul52K3S2EPhfcyqDFT1/RUIZKLTTL2TiIJXOCPOEs3LA/rOe6lCvvNDSH/gPrpz0Huftizl9Xapm3Drq9QIqfQLr7FKa7bhjrduQ4xZCfKgY+A6+CBKG6EXI/5apytqxokFHXd81/ykQ9VkblbgxTTMygIJMErEg0W+GzmM0SVRmgYkVZzsQTU/k4tBo8IqC1Lwpk7hy6zw4Sjzb6cQaS4zzEJFqFM5Pu1Y/6q+CzyJlPSBrQBCw2gX3qgmueTkPiCIv2xtqR67Bwa17WmVrqHaYg/aJgaJNND7v33NoiXnFsI9hy8Vn8Rtrtsn91THrJH5puMULJgtVMlzRbtVsJxwluklE++Da8gKT7ooO+Z25czryVqwfmJFYI4Y9dhLy02X0+bcocFlalmUM24r3MsXOEBgurBEgEs/llCrl9RhX1K3uy+WLS5AdbiIsEBKxxJZwX4rplL3JUai/ZimWSXUX1+gFHzxcswDR+3OgVH3O5YFnDS769ePlG8uLrdZwTDfo8WkIlxO0hkKrr/l7OKtFGefqwn54Ly4nKlJreVp6ArTh6BWFTvztQ0hGQXPT1+6D8zFyfoWk4RdocrbnTDQ+BiP0fe0bwPqfOXqIS84na/eSVWITHhutNfZdAW2fNNoVnE7qYRwD+us+B4kIh2CfEt2hbtXVHbb74iXKWcKGULaWXFt9ueoJKjqo3jzXfKv5KakBo8Lv3WB7Z5F5rBDg+Lzc+ViotYrU7rKSFb0pCHBhQXtGuRb1ASzvj5GrG7yaNkSjnnKYMJAHCcxvdP9Cmv1zCh1L/flMWtnxULfR9wTpBWwuCHhS1f07dmtducdymueKsZzM+FMAyZ6rdjvMLJpBflROAQDNJOxPgzQwmYeLp2gv8LG3Y3G/H0Gf6/hPP8Cxu01ZCDhyBO2U870d5CHFuGIRBdHrhi4HbwkxIgiuKzDoxNFH2oAH7ToBiDdZAG+qUYtw+Ye2hwOVtGnQbAoCIwA3mg4f6hqgFwSlOi50wPh5cX69wS4cNHM2TLtITXeY6Xvw4sLstrFhrBqa+rii6CmahI83gkaFf7W11C3Fn1bD9z/XixJmG/NDmwtTdpoRp0HQP/DbzZLCS8WhGQjo3PrJiLEsl10gpd48tO1VCiiSCI4lVD+63vz1zYFMuJiHpCvuiLQqzFs5MR1ucuowcaIxesnL3mAAWKzt0AdSQ9BqPvBuAxJypLTfM9EQFxO8hObQmMwou4OJOKliSaoaNXJzyKjOzUMT5r2XalS6O+AKGftM571ZAlIJWt4hwN3Z+UFagxV1YUJ/8oFuZtvM8+a6OzFeVq+w5I3756sqU2BqbtLhYX450s17HDaUc+cMXZfOre0Q3SFj6YiVGvkHUim5npeFg3DBfNQmi/QKpf0jKJM+YSOKN3VT0Bb/uZ6VcsK4YAaX/pcq/qAyLjB6dIDqE9qxu1USvCt+S5zAP/DCkJCvoDlS8ck/0pX5SDJhcxdkUGPI/cKzkUkqvpzMX1F1y2RBCU76LkHYhWQvIds/4JMlqi5H2P/cVh00Tu6KryHaOv3/IF4QW+7mPxAi75EI5nOdjg9/SbWtDejiNmd/inD8P7Q80XiN3ookIB5N4QcxbmHpo8PUltURbUXE7N7/QBCGunPuFkwVuEmROUDYWkgh0TqAgWiOk6A2Xmvp1rKXmzfygbnevYD9sqsS+onwZ7euWdzkxK6/6Q+t7grzQbuk7HuQ+ijG/zUzCN7aObEiJs3gmDGKtSvTPg7sR6sWBX68/Y/v/+yy1ZZtu3f3ysohxmCHfguAW/ko5KGUrrRMyOD+wErOAmKP3SV1jyhsZ0DmTxrYd+/KdXctTuDq5xQLtID6NqyBm2walSqFfPSC5BMmAIeer+pauP/7BdEFeHOImytImAfxhFO9MdUokAiSJktNNK8O5e86G6g23IYqP2+EthH7/yRo/JAtTARweIzv7e3hCjZwA4hCIUuxs63wYkh5tlHty+Iy1tn6WzzbGqcdQOd+gXB0meD3t//Qw4dTBvo7jXoEySHZB5IM6/QEi8AO+VOyNG6d9lYlwsJhriVPaN+l7xfS8fYo/bdW0R2hAsp/3pfE+dEk/2OyxYBmq7fIkvmn+S9k5qZg3y156wEOfMEueigqK6JOWStjxk6cJxBeyngtJpjQxWGnS88rMM7Fja8jTuduZ0qMcQk2FpGb4zSTb7BSm5AoAcUqMyNGOixPY6PmzmHtYrGTbIe6QRWjsp+YAiaJl3+Wcu4CZaHZ0+3DcVT1/JHzxohVfUybBTh9Zl7zbCLOZpK3/pJDDVLj1C1k9gH3jFK+DonLalA4ebiZltmI+6Fraf1MROVhtM2uT+WvS5y9jAgSInqnnJDtKdxvECJIKEfPkqEbWu6vT7pCTF3MehSsJsLGMgsZf90YvfrcXGPnw7vJoJxbo2qEv/TDVI+pO3ZHCdQcczD7bXIe3YdFoj3OBn73rgHH/I1YRphuaQjNwpPIT4noGAwC7X0UiZaDbufRmRlYfJNBV8LwDRgVLBhE5A6GgYLxu7IrTRrpyDIjD3ZmmH5Nles8iqLdRW3pme6eDIl4J9dm8IMuBiaH9sd0AnJHnSIlfR/4t455ceiqN6pqF4ceTXm43HqK6i8OPYH+/tv34YifyayfxnpjU6c3005p9PSIoqgXDil/Ovyx92AuEK6O705oh62dv5py8yK7GGs9s8to8mKAzysazNO9rKwDrEm7wItT70jAHJBUs+XVHxv1gGDIeLY12mpOziQClGl1L/EGiRZQoGVSj6zTd0LzpOxxONhxswRxhXDSYGg/cKftrWicb/AgTUR/E4hDY0VzS280lBz61fOlkdH4VYIM8tEZdW1i5i5au4MDRMJqpVv15XjdtWKeEXr0uqyBVTXa6XYYnGw3LvNOxsK+4rbObwDXuourWBGlYRhEDicwL6WAIzR8sd4v0hfp9Y7TtNVU8TXWUqirU3AlB+fwdlEIiewVpug4dnjcnTtYIbTlgYrFklM7ShqdZYlFJKf+w2YxHey+sbf5noVKu80hFii8KWTLGbCiTMDW3poMpTyXNX8IQa4EWolptdn5v8yuX4CNa/MU9oFmoMyYFnK6g6h2c+70hcTljySBxrIBNNp6aEJxFwa4KMkoUGxSfs8rQHrzcNBC8x16EotCO6BjcbIjGMz7pmf2PLz0zhqkE80xjkg9Lho2lHRX1rkBSyI9AX/hXbqhDlCzHwil/IxEjmKD57sVFEt5Oxe9K2QoVKBKH0mgPvvFp9GsnnXl5VvGkQoMGf/E5Eh/XvDbs3PVh1zH2Ij7PBB5g1fslJFWEEpTdniKQycjgVTtgHT3+MuKUlABT9OZVSxwuMVCvzekq1vVHluf2ojy41PSC0QaNM2mfeW579ncRB7q2zUjE2RJzdTTmGN9fRUWP2f/u62M4GEL0ajeQQ6gyLJd1g2OkTcxV0CpK9yxARoRtEDxu9xMJG8hdsoy1BnuVGLqMGLvs17P3YFoj4fFGLJ2D09zlAVdqbJEHSLGWzarpZ3UgAc9sB4UUunsUMOR83gmnQ1lCB0PC+X2aX2Ndkpfj+LCm6WG759UBklQE7bmBXhwuPv2JqKezdkOjJMbYeHH4G6lEHbiNa3xe3RrjsDOmTURY68znndnqpTmqEUTveaIUG7oc4MBfoOi5i1H9AFllJSmOpp/5yfkdPRLaWmNna3qEISA/ZdxRgt2LjW1rfsPe1wRmMsGIKhEtvuqEPE6tv5z99XXc8w/bMInGAq68Np6dA01BJ4EFVpzfwFieUvPGU0GoGEmlBg6D1NLBLljdPYtkWlCOqUTQqglP9nEryV6kl+h7lVsH5huPNN979FisxnDnLgPEzwEBhNwIgeiV69gPkL8A7gk6plN3DijJzNIG3HBGSVwE74Yz4p6E9nQMbqAkKZFi5E/8RpenKLQmAIbHtulfnUv43p1GtKkfLdztRMXL7+qpVQ6GVvIdCxuknyp6eFscZO4C8xkdphn9ie0eLE65bueq1jJJTSu7RrmN3ePjsp9DbBlaJ3WeHn0g4GR8HBmFm8oiZP6mBqPx49MQhsXgtrGBf99EGmHFld7y50ctGmNk3i2aLWxUT13Bzo5UnH/uk+RXOz9cKZMsQWCEVGDFg/DJt4cn5J2Jr61Nx29NbHAukpKbMgFC3f/I1CWcK47mU7MYRZ1X0zKAa5pInGoBSI9JF54GNGbXQn4cqPEfMjH8ji2kuaag3LHhKKHdpRR4saVOvDUiAhTTKEbk0edpV5MP2WVlEu+wrR+qdaJ2yQDDo1UiXvXX2G0vUCg2tu3h5G0+1sHVZkpzjUUiR0J3bNlA0Qh4ZNQOYET4VOZwyJfSWdgor5nTDJYeBbPrt04n6vi68UItLBO2SEVHSq0+J4fTpffS7g1Y7Ac7z0rl4jj41wmf18Udjug0D2rkiClbg09kA9WylR2SY/v8r5oXVpu4Qynnu7MgvV7Zk/g7nNdiELNjYFd6+FQi0QT15qJhVuzWDMj56JMZkVHZn24eJVCRzUAzVkS04SR7kmPn5858I/1P1WQBu949t1BErp/DxWBxGvyvuwPa1FCihQbjaKmW8jtAwkWoxhaIq/Loymb+RoAi9H4tqjHfvAsDARKMgW5qI8VFOisofvaH8PQB0q8EyNpwe0cBgJk0maCkifvdFjI0YxxejKAwqTWaOHe2M85X0uhtCN45H+JnXKnxZseHecbcK2I9hFoWX4ubG4VXg5AFquNhH/bNKDUYX59L2eJ4KSDlzgsVNuVjCIwQvDsHCMuOy/ZcZo3ooO3KXaNYYp/UICKG3d/A16JM5VPeAnVEo5D+RTeNG0infBmV9ga8HrUZaT2Krngf+7+lRjQP+L6XqCoYXcttfInDhX+wS3Lcp3ce4xLwsmR1ClmHPtfwSOfr/O7kSr8hsfez6CpBfhEUFolTyFOzxziGUewsaGdCJvhFCKBlD6sQ7ZHJMBZboUHjJlUeUlFqt1+IOuNWM2qlXSSbQwBPz8orOZCYDBBz8scnpCiob/shHts1v6XWFTLf4kJdQsMHgjhENZerGEWrdTc+yYJnKzEYmGfMX3wsbZkKebK8SdOUysrBa+WlJZM6S2uzRBzG8fcvgM6GxQiOQ3cc1uM6Ld+k4Rjx1p/mVZTThOnHZdTmbjzkWSK/A3pByJXaGB4931Tq3nCZmCgPxkb0rV2ZFvru04KES0aWJYlGjn/zwnToZqr2Y1znDq4+o6+mzj7vpQU7W3EB/2e6WiC1FC46W+z3nYceZwK9locMfFR3z2xQMC6iKmxOvDKNzni8+WayN02v1Zk4LZtgKpqWVvMZtZwfVeN4M/ylcEU0uDOjU/1tIwU3kAsD0N9FpNyBtADMKeVkhppFdCPsyI6O7EGFL1dIDQKjMzLTOceM3XUxIrmxd9Gp9SzTItaYpcpGhNEiJu/oC9rmL7uSjaQe4tpNNxVwoEYCSEjYoJc2Zf27S5m+hIneDJd1psEcNChzMKoBQwLIL6NoZLWoLFJbDolCoKabUR9955QbArNa/ZMZOzv2sts9RZe5rH3fLo0QTKxwqzD5hnLEfN92c1dqbshct10dCvaETRolW3xlujyA4/PCC7Ht4x79JUnNQ1oZLb+AZGexz9mglxIMIfQAO31kvis6m1srul8/4PPQidxYGF2JU6l4cb6jQhj7929b0hEuwQzCVH0d3ablmFjNcdq0IxNqFBtlZuoNmxXGLDrp0nJaJeKEyB5IKa6amNx+Nob1WSYywAKS/mvW6jdNRMUty7/TaFQjgGzq+hKXRAi9Hp8Egivoo6105ZPCC3pheSKWUmeu2f5HV0fjmSzDXPBWXZ95VOCl22cpqxXQBff8o+bmDK5guWc4c2HnrQV9O3OHoSFbq3/v/GAhija6SyQcMKL2l3KqCK210Q7J5DxNrIsO5TezRCOmj/9ESuJPpZvAViQwILu4KX8x817tFWe4uI2onq7cXWOP/kT5OXf1uUDiZib6ljlGmyD1RAcx3w+dj7SAnC6JaKBJydNWJL86UEdxLXIAZSx8zZwk06RBd37iFwrZpf/xIIKud2rVYFMNQ66il4e+VaSmXD2GcFGwXuCNQ9eP7wm6aACcpYB35YNPhrwlDeKxQlEyPYmaBBCVLjp3fP/D3JvZsk7ejvV443yFBwW5gz5/8xRpbquKl3UJKIFU+x091JVs8az3czip8M0IJJUogop7XTHT8l9/Kpl7O889mz+DFa+i1ByvPwX0QUSTp2FhTnE7sYV06RwoWjNIP5Xu7uYzr0njmGB/K1MitDkzM/vtCVh1dlPnzd61BlmVOpBTEtZUcoCaCdDl06yOzhwvUN3XMaKoVjHWJgiJub5449RQMtdVUb4Xk4YW4PBu1SLU4Eun6UwXc5yTBMJH1JRH73CoWDZXpOQDNzgDB2rlIPtPh2xtECRLNJ8fKqU/ey/NEa57ZCY8aAoDjerNTNNJCOzEnnRE5jqo88FSk+Mw15m2x2jpQrLC/n+WmQRWpCkg/7F4dkbLtdQDOIfiq3/ZO7AM+GHu2F6HQSm1qbydJUqRFQtOCH7ubE7Y7rzE/cDWR27QW/mI/66FgpsLogKo5L4fXnXvZ/P/poLogqK/9SPXarVFAdWBMxXOXK8GjVI2dZ09027Vi+onHP2ka4tJdYaRUXA8LLaaIjXAk0Ro2Np/pT0PsuD9nAgBvkuOpvfVzB7Akl4vST0ioKXmvwOUDnY0D9lKDdS9kI/n5YB1tLwIA/+wcKSPKVpVJBxtqAaGm+2gfYWDwtFihgkVS2AgO99Sf2tQpEIF/0HATXNkD34mX0ZOu+8h6/MnpD6sPnsni4DX9VDgxARt8i82aZwPnQxZbLX9x4pQbT36AkG9MDJ2f4Z40eDIzEEqNwt/yTI7CQivOu4u6kUpX3L08ZBqSS3Vus5y4mdRU21wQ+XOscTi1B95QNByQMBb55Jhnd/2RA9xsGxP3mYnJVpTdIz9TJflRO6XAUnY/HM/mf8G49PHwI7QrwOdy1lJ2pFlk6v34KtkdCLT7l7l6ZvBA8kiA9zh8pkaM54syixkQii+AOrWhSgzcaiPCPhjBlvsWpCFpsYtaLMuu6VTCioodSAOjTIbX1nZXUrT83HA3oI0s1j/hSd3N2YxqI9ii/2E5rvUUwmZ9nVEylXyJYr0MhyezqOwAgOPfvAnKvGl1NMHii/Y6k6Jcb0oCZgVqfL7+7G5+wW2ahecS7GfEqnZJu9Q4L7hMVIynn6BAZvGuJfY7hS9ta19tvVSdD/BfU82oteu9GDPzu7sqhkGuitg4v13QbOq59FFcIrRi9DeBGJIqw9MSpnPftsdjzATbtFkWcubNM4F+5tTIAvb/qckBL8feaWiTjNFuB+m1N5dWJsxAsW7N4rCAIBHGauKcfsXBqFR0ek04V6m1m0jJ4vGVgzCnONHER+KMxLBxibSPW3vbDu/RexminaqC4VFO+MkSULIvKl1yOFhiHXwLzbfFkg4jTD0N4Zf1NBOwKdKzYkpC781xymupnvfiFTHcvtPC1pybAI71Dd/iinKHWZzoW4+VrXDzINCsSIbYOMgr2hLn2/gX5MYnUtyqnVhGAkeQ10GGDc0Y21tmxx8srmUCvo0L5a7hu9iTFBIjaEKOy6enVYqi25pqh0YAlDRqcP8TO7bw7zTyucri+Zj8Qf6vLaDrZLHU08oVJczZovHGLuKgfrgef6iAI2oSgvReHMXvKooW9j6FQrdyNJSZXMYn2VcVtkuaL354Tpp4kkU2NCKK3WSUU1gKS0JPKA5O5ezPBcO/vd8yXZKAD2fZGbMh0GgqXHqUc/LYYBuThus8Ph7iVX9JLfDj/lKZ97OaeI2VM+gHsgxuPhD9RixzbeaLFKN2/kgISqPM205/oqVyxDF3Kx+9A8fk8m+f0DaOJrnc/DOYNO29II0L7gcuIHNK4lfyTS+9Z+Ty0hG5cqFUhdRkAYfVP9JAEj+F5brkY7dDQHWpcpKbkityQXNIdBU/ZXJu/cunJpySvHhWhlMJQrActDiNsr03SW+NkRVi1RX1QaH1igFYxPAHXXLIw7/7cd5mXCRA9jVg3iPGwsAdQ/qqwhBavMRJaOpIYCrf8YjQoFzMC/9V0fVa+DGxJOgyQUBZzfTeADq3YVO5DjjAVQPAvVLWJi/RCru48FKIOkAatGL/ovlEW0Ks4T6czKyXTEAU6Pml7hYQmHt9Jgf5EiU6PgbQr527HO42lGAgVE7MjBuHvx3KFPCDpdrquPR78PbECYZiIMsch1/C3s0U7ab42qKXUOLwATdQKz1hroIPTiF8U03TfICxGLdhXcDeEmqb4DAPTuBXSCWZiKgkgZLKIMZS6TeyLQOMZwylu2Y0RkaUylB9dAc3X3Yl8DRQw/bJKHUQucYfGREJ2f5FSU9/K4i1r5q6q6HbYlzIy6cpvN8ysNVPs/zWLstVtHJwmLwQncqsECz9vo4X9zS/cq8ia6LASA4Vv9xeeCpdqUtkooSZAisWRu7iEU6LZmHVAl55RCbaBT1C6Br0EuFDk4yMNUEzwHVW/e9sln/fbfjdh48uQqikJgNUeEo68SG/jye6EoJ69S138ogI3Wjnd5VQIzBRjUj3+uvlq5AzoKoh93onZoNJOR6cd0GUV39mrngp7xyslxIFn8jUUgyj+h0bwK4IBVy2Zg982k6GyKcDEI2J9JS1VUQ062ZpRzQDkDoD5M+O+C40aP8KpH++mETTDZReYs/aIJH/B5FVapjEm/h84+VD9E9SpPtfOBPNTgRQRW4ldFVarZ1gbk4EAtyubBgdH1A950InBeSh781vBqNrnirqrXQcatHS+QV2d8vsF1aFVotmH2mjL7DU21z/lXDxSD6rukR+7KiJsKEELRu1dVi0/QzSOl98cOWdATJavduEohHzJaDy4XCjU8cIH71grYeZDHCGEUGQ/Ls/n7xHt4fq6l9zNTVLLIYRlEAGD1dtwOwPn9OSWqC/wFGebCVmo2AC6wQ9wue3/UHo0z51qvQlwypOMXZIkA9n3fbp7+DpPtQKK09E/ONsHtTtm5NWZ1l9svRhSf/j+rV+zxUIgawLiL5iFIA8QE2FaJ+OHKlT3B8uyk5NWBe48iBQlxG08jkF2RNlPg+43UJN3WRy/w7h/LXvZQV4F2QNIvqo1bKTMS6JFOVtrYd8/TrTHLI2wFYTYy4vwMekd7ieNHx9PI/aufjRsAq7z/XVzmTLMMTl8VSQ+jBZdXuhgnzvem4SxktuLeQn+qO3amxLhoT4SP5G8uEx9WEMHFk808qBOCjm5HAsfOuxMzbTtDIGnHbGifp5wMzPV9xBd3thYkGhHAOeQRnff23XHZ+VfOXXceOj9cuH0mxzr5K3GDZQs63b9EaGK0ow89XFYjFPszVwyCoUij3Yn0/5IlpVCdnp3cuW757ZUgvh7Bda7BzTmm81GI2kqCwD8NU4ML5VoAHup/4DT7aavZgtSgQduzAHfXtNbb8eIfrHJR4qNg36sHIhKvPKRTEl6m6LzG1YNWhICSozjymaZ+9VERAwBNdqo3BoAwEu+W7gUwe9TB82BmRLYBFKsOM3s6x82dCr1HRFuNgvDXrvJSp6+SCoEXPI9UNnB0wIfqmElR7+CFcQawV85dZ8UXvNMyCAAZcuROmIqfjBIIuktvQUBC+ptwe5XHi67TDEIICeros/7tz6USZAMtGMPTUQ1RrI8RVHzaEPZYdfbO6bodmzYHyNOjeeprHAvz5+va+Ty1OZBy+891rI92ILIyL23ecWgY8GuxjJzWfr2sXUCUwMg1ofx/JVxaOYSoEdqI5SlU0n4UPfj/HZfEv4PbtjQ5/4wRk/SPJEJyMDIACBymmPbR1x079LGyfWgxlCQMXHvmEWL0nz5fZJtOmfN4syVhxpTSPw4CVPGz5hiNPsviABR6TJSiUkNu2Mcky22JlAkjWdPOKs6qcictyBGDQ/RukSqNtZBBdiwuj2suHk+pztnr/vtwX2Gj8e6rZ0yEw2nHR2JdrRGCZmm2QAZdwHnIlCGW6ek/O3+l2v2d7g7ejoruspLtz9BEupCCUPHyFMyymvrem1HQhlTHP5GLkwGegzux9F90EZ7pG4QWVcCEmUqY2j+QKROoeqssFB+nlpXg2tqxrM0B/yvDtPVllwOlZjXfc6dTi7mShvVT0dXK2SqKQWP76UtfngxOFVijdGH7SN/gH0JYD9yVkH5Q8Ie+P8jOrjwu4k/MZ7W7jh9dEOSyq/VC6ZCgfMo6X2v41RpfoA/2ix6ZZtl8nGWMOWd6Dp0TxbwaRd1OheluTRuWwEa1r2obpfVkEVcMB9TGhPqsHjcLSZMCaje80euiU3J4lFLvtuAin8qNaXWEb8VDB+gE0y8G67zThYeY4Nd3TeB66C9hlFKwZdIi78YanJgP4QP6eELI+z8cr6gaxFIvAuf+8G+RgZtDsvssyh+ZUKpyuMaar5J6pAT6+fkB9q6x0rCA6CEN77hChiwt3iFwbaIjH3wPYNINDzMzySbyb1IAl2dmfo2PwESKbsJgB6LDsIovSap6HECYdUdYfO6p5RK3Tbohjq0rXZR2CTpXZDhXb4OhtTnvH4SiEq7AUmHrlPysZjz6tRmSfNggeJ6auvulK1Hkmc3WoLouBQeUOilQUVa7ZAeZeveHtZwqYD2qqGUcn0nj3EuHToyRdhAWDo/vr6j729cXJa0OU/9Ths2GZI6QRK2F8lNoMQ7v9J74Z/lCHw1bcH6779pwBOemTqkNHXbeD3HXPurabxk5OasSsIieVgj4usWV3JESuhuexuCFfbjxdHgsWfsFMyOnRRUm+NgdoVj9VUq/nUT6mKV6I+RqYgyhzsPSEbeENAcDzCR/o/WdQre0jxt/XKB8SOiPRnN/BFEQrgv4m/KfgNxBJkSsrX9FSi1b6i5vhIQtkM66OTb3kZSCb84oP+VqsIoVKUK1w4UvCSlwoj0dFg==\",\"st\":1677778673,\"sr\":3326773259,\"cr\":694402945,\"og\":1},\"version\":\"beta\"},\"old_token\":null,\"error\":null,\"performance\":{\"interrogation\":756}}"
    reese84_headers = {
        'authority': 'api.formula1.com',
        'accept': 'application/json; charset=utf-8',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'text/plain; charset=utf-8',
        'origin': 'https://account.formula1.com',
        'pragma': 'no-cache',
        'referer': 'https://account.formula1.com/',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    reese84_response = requests.post(url=reese84_url, headers=reese84_headers, data=reese84_payload)
    reese_84_token = reese84_response.json()["token"]

    # I think both sessionId and uid could be random, but I'm not sure.
    # the other params are timestamp. We should understand if it's ok to have a future timestamp.
    min_unified_session_token10_raw = {"sessionId": str(uuid.uuid4()), "uid": str(uuid.uuid4()), "__sidts__": 1740940828,
                                       "__uidts__": 1740940828}
    # URL Encode the object
    # FIXME
    min_unified_session_token10 = urllib.parse.quote(min_unified_session_token10_raw)

    by_password_url = "https://fantasy.formula1.com/services/session/login"
    by_password_payload = json.dumps({
        "optType": 1,
        "platformId": 1,
        "platformVersion": "1",
        "platformCategory": "web",
        "clientId": 1
    })
    by_password_headers = headers = {
        'authority': 'api.formula1.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'apikey': 'fCUCjWrKPu9ylJwRAv8BpGLEgiAuThx7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': f'notice_preferences=2:; notice_gdpr_prefs=0,1,2::implied,eu; notice_poptime=1650366000000; '
                  f'euconsent-v2=CPnLBYAPnLBYAAvACBENC3CsAP_AAH_AAAAAIzNf_X_fL2vj-_59d_t0eY1L9_63_-wzjheNk-8NSd'
                  f'-X_L8Hp2MyvF36Jq4KuR4ks3LBAQdlHMHcTQmQ4IgVqSLsbk2Mr7NKJ7LEmlMbM2dYGH9vn13T-ZKY70_vf_7z_n'
                  f'-v____77__b-3d0AAAAAAAAAAAAAAIACAAAAAAAAAAAAAAAAABAAAAAAAAABBCoAkw1bgABsSxwJtowigRAjCsJCqBQAUUAwtEBhASuCnZXAR6wiQAIBQBGBECHAFGDAIAABIAkIiAECPBAIACIBAACABUIhAARIAgsAJAwCAAUA0LECKAIQJCDIgIilMCAqRIKCeSIQSA_0MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAA.YAAAAAAAAAAA; '
                  f'cmapi_cookie_privacy=permit 1,2,3; '
                  f'_gcl_au=1.1.2043713071.1676365158; _cb=Bedg6YDSt4uA3K6ua; '
                  f'_evga_95b0={{%22uuid%22:%226d263ad9cbdc4b59%22}}; '
                  f'_rdt_uuid=1676365158025.d140b1ff-8a32-4e45-a659-a096c1d4a952; _schn=_o0tnb; '
                  f'_scid=544d4265-7d1a-4965-94b9-e312b6cc8871; _sfid_8374={{'
                  f'%22anonymousId%22:%226d263ad9cbdc4b59%22%2C%22consents%22:[]}}; notice_behavior=implied,'
                  f'eu; TAconsentID=2801fa4e-46df-4ec8-8391-19b8ca064d40; cmapi_gtm_bl=; '
                  f'_chartbeat2=.1649430790940.1676365199160.0000000000000001.DrWgDRCOtRKOBWaX66BpQUp5DowuCY.1; '
                  f'minUnifiedSessionToken10={min_unified_session_token10} '
                  f'_gid=GA1.2.461696287.1677776338; reese84={reese_84_token}; '
                  f'talkative_ecs__eu__260c846d-7b81-400a-b5e7-e4c3ec819064__widget_is_controlled_fullscreen=0; '
                  f'talkative_ecs__eu__260c846d-7b81-400a-b5e7-e4c3ec819064__push_prompt_dismissed=0; '
                  f'_ga_KT1KWN44WH=GS1.1.1677776341.1.1.1677776385.0.0.0; _uetsid=86511f80b91b11ed872b97f7e90f928d; '
                  f'_uetvid=67a56390b74e11ec9906ff5862072e81; _ga=GA1.2.962319734.1676365158; '
                  f'_ga_VWRQD933RZ=GS1.1.1677776379.2.1.1677776390.0.0.0',
        'origin': 'https://account.formula1.com',
        'pragma': 'no-cache',
        'referer': 'https://account.formula1.com/',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    by_password_response = requests.request("POST", by_password_url, headers=by_password_headers,
                                            data=by_password_payload)
    print(by_password_response.text)
    # From by_password_response get the subscriptionToken

    login_url = "https://api.formula1.com/v2/account/subscriber/authenticate/by-password"
    login_payload = json.dumps({
        "Login": configuration.f1_fantasy.credentials.username,
        "Password": configuration.f1_fantasy.credentials.password,
        "DistributionChannel": "d861e38f-05ea-4063-8776-a7e2b6d885a4"  # Hardcoded at the moment.
    })

# TODO: Append the `login-session={data: {subscriptionToken: <subscriptionToken>}}` to the cookie.
    login_headers = {
        'authority': 'api.formula1.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        # Hardcoded at the moment.
        'apikey': 'fCUCjWrKPu9ylJwRAv8BpGLEgiAuThx7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': f'notice_preferences=2:; notice_gdpr_prefs=0,1,2::implied,eu; notice_poptime=1650366000000; euconsent-v2=CPnLBYAPnLBYAAvACBENC3CsAP_AAH_AAAAAIzNf_X_fL2vj-_59d_t0eY1L9_63_-wzjheNk-8NSd-X_L8Hp2MyvF36Jq4KuR4ks3LBAQdlHMHcTQmQ4IgVqSLsbk2Mr7NKJ7LEmlMbM2dYGH9vn13T-ZKY70_vf_7z_n-v____77__b-3d0AAAAAAAAAAAAAAIACAAAAAAAAAAAAAAAAABAAAAAAAAABBCoAkw1bgABsSxwJtowigRAjCsJCqBQAUUAwtEBhASuCnZXAR6wiQAIBQBGBECHAFGDAIAABIAkIiAECPBAIACIBAACABUIhAARIAgsAJAwCAAUA0LECKAIQJCDIgIilMCAqRIKCeSIQSA_0MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAA.YAAAAAAAAAAA; cmapi_cookie_privacy=permit 1,2,3; _gcl_au=1.1.2043713071.1676365158; _cb=Bedg6YDSt4uA3K6ua; _evga_95b0={{%22uuid%22:%226d263ad9cbdc4b59%22}}; _rdt_uuid=1676365158025.d140b1ff-8a32-4e45-a659-a096c1d4a952; _schn=_o0tnb; _scid=544d4265-7d1a-4965-94b9-e312b6cc8871; _sfid_8374={{%22anonymousId%22:%226d263ad9cbdc4b59%22%2C%22consents%22:[]}}; notice_behavior=implied,eu; TAconsentID=2801fa4e-46df-4ec8-8391-19b8ca064d40; cmapi_gtm_bl=; _chartbeat2=.1649430790940.1676365199160.0000000000000001.DrWgDRCOtRKOBWaX66BpQUp5DowuCY.1; '
                  f'minUnifiedSessionToken10={min_unified_session_token10}; _gid=GA1.2.461696287.1677776338; '
                  f'reese84={reese_84_token}; talkative_ecs__eu__260c846d-7b81-400a-b5e7-e4c3ec819064__widget_is_controlled_fullscreen=0; talkative_ecs__eu__260c846d-7b81-400a-b5e7-e4c3ec819064__push_prompt_dismissed=0; _ga_KT1KWN44WH=GS1.1.1677776341.1.1.1677776385.0.0.0; _uetsid=86511f80b91b11ed872b97f7e90f928d; _uetvid=67a56390b74e11ec9906ff5862072e81; _ga=GA1.2.962319734.1676365158; _ga_VWRQD933RZ=GS1.1.1677776379.2.1.1677776390.0.0.0',
        'origin': 'https://account.formula1.com',
        'pragma': 'no-cache',
        'referer': 'https://account.formula1.com/',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    login_response = requests.post(url=login_url, headers=login_headers, data=login_payload)
    # Extract F1_FANTASY_007 cookie from the response.

    chrome_options = uc_chrome_options()
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    seleniumwire_options = {"connection_keep_alive": True, "disable_encoding": True}
    driver = ChromeDriver(
        options=chrome_options, seleniumwire_options=seleniumwire_options
    )

    log.info("Scheduling restart")
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=driver.reboot, trigger="interval", hours=24)
    scheduler.start()

    log.info("Performing login")
    driver.login(
        url=configuration.f1_fantasy.login_url,
        credentials=configuration.f1_fantasy.credentials,
    )
    cookies = driver.get_player_cookie()
    driver.close()

    fantasy_bot = Bot(
        api_key=configuration.bot.api_key, db_config=configuration.db_config
    )

    log.info("Loading drivers")

    f1_drivers_req = requests.get(
        url="https://fantasy.formula1.com/feeds/drivers/1_en.json?buster=20230227110410",
        cookies={"Cookie": cookies}
    )

    f1_drivers = f1_drivers_req.json()["Data"]["Value"]
    f1_all_drivers = {}
    for f1_driver in f1_drivers:
        if f1_driver["PositionName"] == "DRIVER":
            f1_all_drivers[int(f1_driver["PlayerId"])] = f1_driver["FUllName"].split(" ")[1]

    log.info("Creating F1 Fantasy base HTTP client")
    f1_fantasy_http_client = HTTPClient(
        base_url="https://fantasy.formula1.com",
    )
    log.info("Creating Season Service")
    f1_fantasy_service = F1FantasyService(
        http_client=f1_fantasy_http_client,
        logger=create_logger(
            "f1-fantasy-service", level=configuration.log.log_level, format=LOG_FORMAT
        ),
        cookies=cookies,
        league_id=configuration.f1_fantasy.league_id,
    )

    log.info("Telegram registering handlers")
    handlers = get_handlers(
        drivers=f1_all_drivers,
        f1_fantasy_service=f1_fantasy_service,
    )
    for handler in handlers:
        fantasy_bot.dispatcher.add_handler(handler=handler)

    log.info("Starting bot")
    fantasy_bot.start_bot()
