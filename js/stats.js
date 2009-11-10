var  ofc = $.query.get('ofc');

function createGrid(){
	$('#tt').datagrid({
		title: 'IP Address',
		width: 800,
		height: 350,
		striped: true,
		url: ofc,
		fields: [
			'orderNo','employee','country','customer','y2005','y2006','y2007','y2008','deliveryDate'
		],
		columns: [[
			{title:'单据编号',field:'orderNo',rowspan:2,width:100},
			{title:'业务员',field:'employee',rowspan:2,width:100},
			{title:'单据信息',colspan:7}
		],[
			{title:'国家',field:'country',width:100},
			{title:'客户',field:'customer',width:100},
			{title:'2005',field:'y2005',width:60},
			{title:'2006',field:'y2006',width:60},
			{title:'2007',field:'y2007',width:60},
			{title:'2008',field:'y2008',width:60},
			{title:'日期',field:'deliveryDate',width:100}
		]],
		sortName: 'orderNo',
		sortOrder: 'asc',
		pagination: true/*,
		toolbar: [{
			text:'新增',
			iconCls:'icon-add',
			handler: newSale
		},{
			text:'修改',
			iconCls:'icon-edit',
			handler: editSale
		},'-',{
			text:'删除',
			iconCls:'icon-remove',
			handler: destroySale
		}]*/
	})
}

var url;

function createDialog(){
	$('#dlg').dialog({
		closed: true,
		width: 400,
		height: 420,
		modal: true,
		buttons:{
			'保存': function(){
				$.ajax({
					url: url,
					type: 'post',
					data: $('#form1').serialize(),
					dataType:'json',
					success:function(data){
						if (data.success){
							$('#tt').datagrid('reload');	// 刷新列表数据
							$('#dlg').dialog({closed:true});// 关闭对话框
						} else {
							$.messager.alert('警告', data.msg, 'error');
						}
					}
				})
			},
			'取消': function(){
				$('#dlg').dialog({closed:true});
			}
		}
	})
}

function newSale(){
	$('#dlg').dialog({
		title: '新建销售数据',
		closed: false,
		href: '/test9/sale/create'
	});
	url = '/test9/sale/save';
}
function editSale(){
	var record = $('#tt').datagrid('getSelected');
	if (record){
		$('#dlg').dialog({
			title:'修改销售数据',
			closed:false,
			href:'/test9/sale/edit/'+record.orderNo+'?t='+new Date().getTime()
		});
		url = '/test9/sale/update/'+record.orderNo;
	} else {
		$.messager.alert('警告', '请先选择数据', 'warning');
	}
}
function destroySale(){
	var record = $('#tt').datagrid('getSelected');
	if (record){
		$.messager.confirm('删除确认','是否真的删除所选记录？', function(r){
			if (r){
				$.ajax({
					url:'/test9/sale/destroy/'+record.orderNo,
					type:'post',
					dataType:'json',
					success:function(){
						$('#tt').datagrid('reload');	// 刷新列表数据
					}
				})
			}
		});
	} else {
		$.messager.alert('警告', '请先选择数据', 'warning');
	}
	
}

$(function(){
	createGrid();
	createDialog();
})