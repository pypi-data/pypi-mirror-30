define(["jquery","cytoscape","cytoscape-dagre","dagre","cytoscape-expand-collapse"],function(
  $,
  cytoscape,
  cytoscape_dagre,
  dagre,
  expand_collapse
){

  cytoscape_dagre( cytoscape, dagre ); // register extension
  expand_collapse( cytoscape, $ ); // register extension

  return {

    rest_controller: {
      server: undefined,

      connect: function(server){
        this.server = server
      },

      //read

      state: function(){
        return $.ajax({
          method: 'GET',
          url: this.server + '/state'+'?_=' + new Date().getTime(),
        })
      },


      node: function(nodeid){
        return $.ajax({
          method: 'GET',
          url: this.server + '/state/node/'+nodeid,
        })
      },


      rule: function(ruleid){
        return $.ajax({
          method: 'GET',
          url: this.server + '/state/rule/'+ruleid,
        })
      },


      applicable_rules: function(){
        return $.ajax({
          method: 'GET',
          url: this.server + '/ctrl/read/applicable_rules',
        })
      },

      submittable_nodes: function(){
        return $.ajax({
          method: 'GET',
          url: this.server + '/ctrl/read/submittable_nodes',
        })
      },


      //write
      reset_nodes: function(nodes){
        console.log('reset_nodes from ' + this.server)
      },

      submit_nodes: function(nodes){
        return $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/ctrl/write/submit_nodes",
          data: JSON.stringify({nodeids: nodes}),
          dataType: "json"
        });

        console.log('submit_nodes ' + nodes + ' to ' + this.server)
      },

      reset_nodes: function(nodes){
        return $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/ctrl/write/reset_nodes",
          data: JSON.stringify({nodeids: nodes}),
          dataType: "json"
        });
      },

      apply_rules: function(rules){
        return $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/ctrl/write/apply_rules",
          data: JSON.stringify({ruleids: rules}),
          dataType: "json"
        });

        console.log('apply_rules   ' + rules + ' to ' + this.server)
      },
    },


    yadage2cytodata: function(data){
      var cytodata = {
        nodes: [],
        edges: [],
      }

      var stages = new Set();
      var scopes = new Set();


      $.each(data.dag.nodes, function(){
        var absstage = this.task.metadata.wflow_offset+"#"+this.task.metadata.wflow_stage
        stages.add(absstage)
        var abspath = ''
        // console.log(this.task.metadata.wflow_offset)
        // console.log(this.task.metadata.wflow_offset.split('/'))
        $.each(this.task.metadata.wflow_offset.split('/'),function(){
          if(this!=""){
            abspath = abspath + '/' + this
          }
          else{
            // console.log('root path')
          }
          scopes.add(abspath)
          // console.log('path: ' + abspath)
        })
      })

      scopes.forEach(function(v,v,s){
        // console.log('scope ' + v)

        if(v=='') return;

        var last_part = v.split('/').slice(-1)

        var label = isNaN(parseInt(last_part))? last_part : "idx: " + last_part;

        var scope_data = {data: {
          yadage_type: 'scope',
          details: this,
          id: v,
          label: label
        },
        }

        if(v!=""){
          var parent = v.split('/').slice(0,-1).join('/')
          parent = parent
          // console.log('parent: '+ parent)
          if(parent!=''){
            scope_data.data.parent = parent
          }
        }
        else{
        }
        cytodata.nodes.push(scope_data)

      })

      stages.forEach(function(v,v,s){
        cytodata.nodes.push({data: {
          yadage_type: 'stage',
          details: {
            name: v.split('#')[1],
            scope: v.split('#')[0]
          },
          id: v,
          label: v.split('#')[1],
          parent: v.split('#')[0] != '' ? v.split('#')[0] : undefined
        },
        style: {
          'border-style': 'dashed'
        }
        })
      })


      var state_color = {
        SUCCESS: 'green',
        FAILED: 'red',
        DEFINED: 'grey',
        RUNNING: 'yellow'
      }

      $.each(data.dag.nodes, function(){
        var absstage = this.task.metadata.wflow_offset+"#"+this.task.metadata.wflow_stage
        stages.add(absstage)
        scopes.add(this.task.metadata.wflow_offset)

        is_output = this.name.startsWith('output')
        is_init = this.name.startsWith('init')
        is_special = is_output || is_init

        console.log('color: ' + state_color[this.state])

        cytodata.nodes.push({
          data: {
            yadage_type: 'node',
            details: this,
            id: this.id,
            label: is_special ? '' : this.name,
            parent: absstage
          },
          style: {
            'background-color': state_color[this.state],
            shape: is_init ? 'diamond' : is_output ? 'ellipse' : undefined,
            width: is_special ? '10' : undefined,
            height: is_special ? '10' : undefined
          }
        })
      })


      $.each(data.dag.edges, function(){
        cytodata.edges.push({
          data: {
            source: this[0], target: this[1]
          }
        })
      })

      return cytodata
    },

    cystyle: function(){
      return [
        {
          selector: 'node',
          style: {
            'width': 'label',
            'shape': 'roundrectangle',
            'label': 'data(label)',
            'text-halign': 'center',
            'text-valign': 'center'
          },
        },
        {
          selector: '$node > node',
          style: {
            "label": ""
          }
        },

        {
          selector: ':parent',
          style: {
            'font-size': 10,
            'color': 'grey',
            'text-margin-y': 10,
            'text-margin-x': 50,
            'text-valign': 'top',
            'text-halign': 'left',
            'background-opacity': 0.333
          }
        },
        {
          selector: "node.cy-expand-collapse-collapsed-node",
          style: {
            'text-halign': 'center',
            'text-valign': 'center',
            "width": 'label',
            "label": "data(label)",
            "background-color": "steelblue",
            "shape": "roundrectangle"
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1,
            'mid-target-arrow-shape': 'triangle',
            'line-color': 'grey',
            'target-arrow-color': 'grey',
            'curve-style': 'bezier',
            'control-point-step-size': '15px'
          }
        },
        {
          selector: 'edge.cy-expand-collapse-meta-edge',
          style: {
            'width': 2,
            'line-color': 'steelblue',
            'curve-style': 'bezier',
            'control-point-step-size': '15px'
          }
        },
        {
          selector: ':selected',
          style: {
            "border-width": 3,
            "border-color": 'black'
          }
        }
      ]
    },

    cy: undefined,
    collapse_api: undefined,

    nodeSelectCallback: function(evt){
      console.log('why?')
      console.log(evt)
    },

    stageSelectCallback: function(evt){
      console.log('stage selected')
    },

    redraw_graph: function(data){
      this.yadage_state = data || this.yadage_state
      this.cy.startBatch()
      this.cy.remove('node')

      var cd = this.yadage2cytodata(this.yadage_state)
      this.cy.add(cd.edges.concat(cd.nodes))
      this.cy.layout(this.layout).run()

      this.cy.endBatch()
    },

    layout: {
      name: 'dagre',
      rankDir: 'TB',
      animate: false,
      fit: true
    },

    initialize_graph: function(element){




      this.cy = cytoscape({
        layout: this.layout,
        container: element,
        boxSelectionEnabled: false,
        autounselectify: true,

        style: this.cystyle(),
        elements: []

      });

      this.cy.on("click",'node[yadage_type = "node"]',this.nodeSelectCallback);
      this.cy.on("click",'node[yadage_type = "stage"]',this.stageSelectCallback);

      this.collapse_api = this.cy.expandCollapse({
        layoutBy: this.layout,
        fisheye: false,
        animate: false,
        undoable: false
      });

      // this.collapse_api.collapseAll()
    }
  }

})
