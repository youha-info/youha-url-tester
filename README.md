## Usage

```yaml
  - name: URL Tester
    uses: youha-info/youha-url-tester@master
    env:
        INPUT_BASE_URL: "https://test.net"
        INPUT_URIS: "/api/users,/api/articles"
        INPUT_USER_POOL_ID: "AWS user pool ID"
        INPUT_APP_CLIENT_ID: "AWS app client ID"
        INPUT_TEST_USER_ID: "testuser@test.net"
        INPUT_TEST_USER_PASSWORD: "your_password"
    if: ${{ always() }}
```

```yaml
  - name: Get URIs
    id: get_uris
    run: |
      echo ::set-output name=uris::/api/v1/users,/api/v1/articles 
      
  - name: URL Tester
    uses: youha-info/youha-url-tester@master
    env:
        INPUT_BASE_URL: "https://target-api.base.net"
        INPUT_URIS: ${{ steps.get_uris.outputs.uris }}
        INPUT_USER_POOL_ID: ${{ secrets.INPUT_USER_POOL_ID }}
        INPUT_APP_CLIENT_ID: ${{ secrets.INPUT_APP_CLIENT_ID }}
        INPUT_TEST_USER_ID: ${{ secrets.INPUT_TEST_USER_ID }}
        INPUT_TEST_USER_PASSWORD: ${{ secrets.INPUT_TEST_USER_PASSWORD }}
    if: ${{ always() }}
```
