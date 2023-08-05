[![WhaTap Logo](https://login.whatap.io/static/whatap_logo.png)](https://www.whatap.io/)
# WhaTap for python

Whatap allows for application performance monitoring.


# 개발 환경 : python 3.6.0 / go 1.8.3 (osX)

## python 가상 환경 만들기 (macOSX기준)

### pyenv 패키지 설치

```shell
$ brew update
$ brew install pyenv

```

### pyenv 패키지 사용

```shell
$ pyenv install -list # 설치 가능한 파이썬 목록 확인.x
$ pyenv install 3.6.0 # 개발 환경에 필요한 파이썬 버전을 설치
$ pyenv versions # 설치되어 있는 파이썬 버전들 확인
$ pyenv version # 현재 설정되어 있는 파이썬 버전
$ pyenv global 혹은 local 3.6.0 # 설치되어 있는 파이썬 버전을 현재 사용할 파이썬 버전으로 설정
```

### 가상 환경 디렉토리 생성 & 사용

```shell
$ pyvenv env # 가상 환경 디렉토리 만들기
$ . env/bin/activate # 가상 환경 사용
$ deactivate # 가상 환경 빠져나오기
```

## 필수 패키지 설치

```shell
(env)$ pip install -r requirements.txt
```


## Deploy

### 버전 정책
실제 배포 되는 버전 정책은 `0.0.1.[YYYYMMDD]_##`

### 최초 등록

```shell
$ python setup.py register -r pypi 혹은 testpypi # 최초 패키지 등록. 필요에 따라 testpypi 등록
```

### python 명령어 사용

#### 빌드

```shell
$ python setup.py build
```

#### 개발자 테스트(create pip script)

```shell
$ python setup.py develop
```

### shell스크립트 사용


#### update go agent 
* 스크립트 실행 위치는 python-apm/이어야 합니다.

```shell
$ ./compile_goagent.sh [options]

ex) ./compile_goagent.sh $GOPATH $$OUTPUTPATH
```


#### packaging & distribution 
* 스크립트 실행 위치는 python-apm/이어야 합니다.

```shell
$ ./deploy_pypi.sh [options]

ex) ./deploy_pipy.sh testpypi 0.0.1dev166 true true
ex) ./deploy_pipy.sh pypi 0.0.1166 true true
```
#### 사용 예
ex)

```shell
./compile_goagent.sh $GOPATH $OUTPUTPATH
./deploy_pipy.sh testpypi 0.0.1dev231 true true
```
## Agent 동작 테스트

### pip

#### Test Pypi
* https://testpypi.python.org/pypi
* 배포 전 whatap/build.py 버전을 올려야 합니다.
* index-servers = testpypi 설정합니다.

```shell
$ pip install -i https://testpypi.python.org/pypi whatap-python # local test
```

#### Pypi 
* https://pypi.python.org/pypi
* 배포 전 whatap/build.py 버전을 올려야 합니다.
* index-servers = pypi 설정합니다.

```shell
$ pip install whatap-python # local test
```

### By Git

```shell
$ pip install -e git+git@gitlab.whatap.io:whatap-inc/python-apm.git#egg=whatap
```


## Code Test

```shell
$ flake8
```