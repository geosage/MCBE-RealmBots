import requests
import json

# Specify the endpoint URL
url = 'https://profile.xboxlive.com/users/gt(xpuzzleTTVx)/profile/settings'

# Set the necessary headers
headers = {
    "x-xbl-contract-version": "2",
    "content-type": "application/json",
    "Authorization": "XBL3.0 x=13707822975263678889;eyJlbmMiOiJBMTI4Q0JDK0hTMjU2IiwiYWxnIjoiUlNBLU9BRVAiLCJjdHkiOiJKV1QiLCJ6aXAiOiJERUYiLCJ4NXQiOiIxZlVBejExYmtpWklFaE5KSVZnSDFTdTVzX2cifQ.jqn_krij83fu0GNOSHhTXKJ9l44liMVgptEH41Lxcu9N0mrMGK6HD5_jp8fwblHfah-5mN4jFuGEtk3XX7OZw_6aVgLi3mNJHXH63dJRJUP9ipbmiKCrxJcqHyRQApYqQTScU08bkLagrdnM2btH83OuExPQJ9C20n40Cbhw5FE.XzCusJRd8Zd_R3QVtVD3Tg.uT5WJHuum0KVZ2iJ8-4IBev0i1rQJVugAiKmmhbHkKmGVHVxCz5c4XH67rpZKPBj1bap7O8e53BmWQQZQqJIZTq_ovPh_FyntUYFopHtWCvNO3beLPA66OlvacIlXYdverpGnn38uUUFbVC2gtZOTKLbvhQbpAp0YhUPeHdoTzjxsj-Hif4qZG2WrIUtnwNPjGKwWas7zOaItPCIQRtVwa3kxdIE8k5NCpR19gmA-jAdHu4TOyNMZ1hpVfpS3lHiRU2qGeJ_j_IBWcVuvC2AepNlOPwul2taFZRPhCuGDUG_C102iPAVv8VCShoL0cHEwyIL_DmSY2OZy0Ph-WYBymod3Xh9WXymjt0sKwl4P9VudjO5JMlqeesRsS8LhhdQBLhXqmWww6A2_RGt9y2o2VkBP7z1ZNFL5neV2L3QsfOy3lkBxgNmp2e7YGNdLn7xViLhbPYsU8X8_34Lop5Mpctp-AzPnBAw1XfdSx8Ij9a3JoQZQCAIricqli3t5WK3T7UuL7Dbt4mWljF7jgUjujRU3AGkkVTz8BezBy6Ay5GU7GhSWnhcqQFVTigexi-2iTC8UT6bw1n7Wm-OPZ2j-79Qa8UDSx1-tGmzQavXJCAYOQDUJWlYswVfD358YR1eXuaoUhXjK_r6bLnAfbZZIpBi8IvtCaNhPZ_qRswazQrvI1CnSRwKpT8jH3vtL0Pwtk9cXimfHU5yHp8qvw0X9UKV4-Ps_K9vRTHZXN1x0NeBSrSCy8Ss4oBfd8gGY7OcMS_9M1hoYJa0sX-unuV-8xqOIpSHlhOeJ3fHrMn1uWqcL6lNbD2W2LZjNltS0VYbsPJAzupFNIrMzXku0mlrShu3P9RdR2mijAMWXDII8cmOquTDAqkxomt6vbnOW3BkFiDAAYtxiNlyrNPxpUiFGQYUgWFSOUGKAOhQDOXVCw3MEyrwJCwByaLMXAUzxeUVpM5xipNQ1JuxBv2DwU_PLekXZYv7lO8DtFtf_fUCQdJiX6y7-th5lwLBSi1Iu7edkq-PT1ZZwslMfYiSfuNVhjz4gNwKDzsg9MUyJJDuUs5QamlbpeEHlaa2mOTr2hw6J6Dsjx1-olE-BgcBzOlPMiTDbcquChK7FRHwDAC7NURmKUBccnijsWc2DzhRvsa2g4LXev5NLIVxDMU0zDW9Lh0-r5S76nRTdDd1xgOXV1IeHMZxVAptU40P3m90Y4ak5-rlZT6yePvub-K8-G08M2Cg0p8cg6OIyDx-RJe1KZAFjYpOwkrD-sF_IeilhNjPAPQ27f5aqWdJyJRkzVWIdwIeL8b7El7w5IN79EFSr4mtEky-xe2SVqW60kkOSJOpifroNqI6kGTm0FFFOodRGN2ZaLsVvXDC5rE-R5fGa_2I3PLtDxUSbv74DusgbhqTnlV1vAST--AQtDu7__KHX2jGfBurbqZRtW0yexJqR6E.MHhPshTuZLmTxvFxKfUUoMTF09rpiwDHMoESuLfTv9c"
}

# Set the request body (payload)
payload = {
    "userIds": [
        "326136"
    ],
    "settings": [
        "GameDisplayName",
        "AppDisplayName",
        "Gamerscore"
    ]
}

# Send the POST request
response = requests.get(url, headers=headers)

# Check the response status code
if response.status_code == 200:
    response_json = response.json()

    # Convert the JSON to a readable format
    formatted_response = json.dumps(response_json, indent=4)
    print(formatted_response)
else:
    print("Request failed with status code:", response.status_code)
