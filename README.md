## Infra CVE Manage Server

Infra CVE Manager Service（简称 icms）是为 Infrastructure 团队（简称 Infra）开发的一款服务。icms 通过每日收集 Infra 纳管的所有服务涉及的第三方包，与 Vtopia 提供的漏洞数据库进行匹配，找出服务第三方包涉及的 CVE 漏洞，并通知相关维护者跟踪处理。

  

### 服务组件

- OPS

	OPS是Infra自建的一个运维平台，也是基础设施运维的一个数据中心。其为服务提供项目查询接口。

- trivy

	[trivy](https://trivy.dev/)是一个全面的多功能扫描器，trivy拥有查找安全问题的扫描器，并定位可以找到这些问题的位置。trivy可扫描的目标包括容器镜像、文件系统、Git远程库、k8s、AWS等。本服务中使用了trivy扫描Git远程库的能力。

	为保证服务顺利运行，需要安装trivy，安装步骤如下：

	- 下载trivy的压缩包

	执行 `wget https://github.com/aquasecurity/trivy/releases/download/v0.42.1/trivy_0.42.1_Linux-64bit.tar.gz`

	- 解压压缩包

	执行 `tar -zxf trivy_0.42.1_Linux-64bit.tar.gz` ，解压后执行 `mv ./trivy /usr/bin`

- CVE Manager

	CVE Manager集多个开源社区的第三方组件为一体，对接中科院的漏洞感知工具vtopia，并对接收到的CVE漏洞做匹配、分发以及进度跟踪。本服务中，使用了CVE Manager封装的vtopia漏洞查询接口。


### 服务流程

1. 从OPS获取项目仓库信息

	通过OPS提供的接口获取基础设施维护的所有工程的仓库链接及维护者信息。

2. 使用trivy获取各个仓库的packages

	通常，可以使用命令 `trivy repo project_address --list-all-pkgs --format json --output project_name.json` 可以将单个仓库的扫描信息以json文件导出。在本服务中，部分仓库未完全开源，执行上述命令可能会因权限问题导致获取失败，故统一拉取仓库代码，通过trivy fs扫描文件的方式导出该json文件。以项目 https://github.com/opensourceways/issue_pr_board 为例，在拉取仓库代码后，通过命令`trivy fs issue_pr_board --list-all-pkgs --format json --output issue_pr_board.json`导出issue_pr_board.json，下面展示了issue_pr_board.json的片段。

	```json

	{

	"SchmeVersion": 2,

	"ArtifactName": "github.com/opensourceways/issue_pr_board",

	"ArtifactType": "repository",

	"Metadata": {

	"ImageConfig": {

	"architecture": "",

	"created": "0001-01-01T00:00:00Z",

	"os": "",

	"rootfs": {

	"type": "",

	"diff_ids": null

	}

	},

	"config": {}

	},

	"Results": [

	{

	"Target": "go.mid",

	"Class": "lang-pkgs",

	"Type": "gomod",

	"Packages": [

	{

	"ID": "github.com/astaxie/beego@v1.12.3",

	"Name": "github.com/astaxie/beego",

	"Version": "1.12.3",

	"Licenses": [

	"Apache-2.0"

	],

	"DependsOn": [

	"golang.org/x/crypto@v0.0.0-20200622213623-75b288015ac9",

	"github.com/hashicorp/golang-lru@v0.5.4",

	"github.com/go-sql-driver/mysql@v1.5.0",

	"github.com/pkg/errors@v0.9.1",

	"github.com/shiena/ansicolor@v0.0.0-20151119151921-a422bbe96644",

	"github.com/prometheus/client_golang@v1.7.0",

	"gopkg.in/yaml.v2@v2.2.8"

	],

	"Layer": {}

	},

	{

	"ID": "github.com/beorn7/perks@v1.0.1",

	"Name": "github.com/beorn7/perks",

	"Version": "1.0.1",

	"Licenses": [

	"MIT"

	],

	"Indirect": true,

	"Layer": {}

	},

	{

	"ID": "github.com/cespare/xxhash/v2@v2.1.1",

	"Name": "github.com/cespare/xxhash/v2",

	"Version": "2.1.1",

	"Licenses": [

	"MIT"

	],

	"Layer": {}

	}

	]

	}

	```

	在trivy生成的json文件中，Results的Packages列出了仓库中所有的依赖文件以及依赖关系。在Results中，Vulnerabilities则是trivy扫描出的CVE漏洞，不过由于无法验证完整性和准确性，暂不使用Vulnerabilities提供的数据。


3. CVE匹配

	通过社区CVE Manager提供的vtopia CVE漏洞查询API获取社区全量漏洞库。

	分析Infra所有维护工程的包，并与上述获取到的全量漏洞库进行比对，匹配Infra维护工程存在的CVE漏洞。

	

4. CVE跟踪

	社区CVE Manager在匹配到某个包存在漏洞后，会通过机器人在该包对应的仓库下提交issue，通过该issue对包进行CVE漏洞跟踪。
	
	与之不同的是，本服务会每日定时刷新当日Infra所匹配到的CVE，并将涉及到的CVE通过邮件分别发送给各个负责人。

5. CVE看板

	本服务每日会从0点开始更新匹配到的CVE，并提供了简易的[查看面板](https://icms.test.osinfra.cn/vulnerabilities/)。

