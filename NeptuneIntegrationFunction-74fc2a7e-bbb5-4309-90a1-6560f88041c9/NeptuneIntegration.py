import boto3
from gremlin_python.driver import client, serializer
import time

def handler(event, context):
    def calculate_score(carrier_data, is_hazmat, is_prime):
        """Calculate a weighted score for carrier recommendation."""
        try:
            price = float(carrier_data['price'])
            
            # Fix delivery time parsing
            delivery_time = carrier_data['delivery_time']
            delivery_range = [int(d.strip().split()[0]) for d in delivery_time.split('-')]
            delivery_days = sum(delivery_range) / len(delivery_range)
            
            emissions = float(carrier_data['emissions'].split()[0])
            
            weights = {
                'price': 0.35,
                'time': 0.30,
                'emissions': 0.20,
                'service': 0.15
            }
            
            if is_hazmat:
                weights['service'] += 0.10
                weights['price'] -= 0.05
                weights['time'] -= 0.05
                
            if is_prime:
                weights['time'] += 0.05
                weights['price'] -= 0.05

            # Normalize scores (higher is better)
            max_price = 1000.0
            max_days = 30.0
            max_emissions = 5.0
            
            price_score = (max_price - price) / max_price
            time_score = (max_days - delivery_days) / max_days
            emissions_score = (max_emissions - emissions) / max_emissions
            
            # Service score based on capabilities
            service_score = 0.5  # Base score
            if is_hazmat and carrier_data.get('hazmat_handling') == "Certified":
                service_score += 0.25
            if is_prime and carrier_data.get('prime_benefits') == "Applied":
                service_score += 0.25

            # Calculate final weighted score
            final_score = (
                price_score * weights['price'] +
                time_score * weights['time'] +
                emissions_score * weights['emissions'] +
                service_score * weights['service']
            ) * 100  # Convert to percentage
            
            return round(final_score, 2)
        except Exception as e:
            print(f"Error in score calculation: {str(e)}")
            return 0.0

    # Neptune connection setup
    neptune_endpoint = 'db-neptune-1.cluster-cro660am4yd1.us-west-2.neptune.amazonaws.com'
    port = 8182
    gremlin_client = client.Client(
        f'wss://{neptune_endpoint}:{port}/gremlin',
        'g',
        message_serializer=serializer.GraphSONSerializersV2d0()
    )
    print("Neptune Client Initialized")

    def execute_query(query, retries=3):
        """Execute Gremlin query with retry logic."""
        for attempt in range(retries):
            try:
                result = gremlin_client.submit(query).all().result()
                return result
            except Exception as e:
                print(f"Query failed: {query}, Error: {e}")
                if attempt < retries - 1:
                    print("Retrying query...")
                    time.sleep(2 ** attempt)
                else:
                    raise e

    def clean_string(s):
        """Clean string for query safety."""
        if isinstance(s, str):
            return s.replace("'", "\\'").replace('"', '\\"')
        return str(s)

    try:
        # Extract input data
        carrier_pricing = event['carrier_pricing']['shipping_options']
        negotiated_prices = event['negotiated_prices']
        order_id = event['order_id']['S']
        is_hazmat = event.get('hazard_classification', 'NON_HAZARDOUS') == 'HAZARDOUS'
        is_prime = event.get('customer_prime_member', {}).get('S', 'No') == 'Yes'

        # Create Order vertex
        order_creation_query = f"""
        g.V().has('Order', 'id', 'Order_{order_id}').fold().coalesce(
            unfold(),
            addV('Order')
             .property('id', 'Order_{order_id}')
             .property('hazmat', '{str(is_hazmat).lower()}')
             .property('prime', '{str(is_prime).lower()}')
        )
        """
        execute_query(order_creation_query)

        # Process carriers
        for carrier in carrier_pricing:
            carrier_name = clean_string(carrier['carrier'])
            price = float(carrier['price'].strip('$'))
            delivery_time = clean_string(carrier['delivery_time'])
            emissions = float(carrier['co2_emissions'].split()[0])
            transport_mode = clean_string(carrier['mode'])
            
            negotiated_price = next(
                (item['negotiated_price'] for item in negotiated_prices if item['carrier'] == carrier_name),
                price
            )

            # Create Carrier vertex
            carrier_query = f"""
            g.V().has('Carrier', 'name', '{carrier_name}').fold().coalesce(
                unfold(),
                addV('Carrier')
            )
            .property('name', '{carrier_name}')
            .property('base_price', {price})
            .property('delivery_time', '{delivery_time}')
            .property('co2_emissions', {emissions})
            .property('transport_mode', '{transport_mode}')
            """
            execute_query(carrier_query)

            # Create or update edge
            edge_query = f"""
            g.V().has('Carrier', 'name', '{carrier_name}')
            .as('c')
            .V().has('Order', 'id', 'Order_{order_id}')
            .coalesce(
                __.inE('SERVES').where(outV().as('c')),
                addE('SERVES').from('c')
            )
            .property('negotiated_price', {negotiated_price})
            .property('delivery_time', '{delivery_time}')
            .property('transport_mode', '{transport_mode}')
            """
            execute_query(edge_query)

        # Calculate option types
        option_type_query = """
        g.V().hasLabel('Carrier')
         .project('name', 'option_type')
         .by(values('name'))
         .by(
            choose(
                values('base_price').is(lt(300)),
                constant('Cost-effective'),
                choose(
                    values('base_price').is(lt(500)),
                    constant('Balanced'),
                    constant('Urgent')
                )
            )
         ).dedup()
        """
        option_type_neptune = execute_query(option_type_query)

        # Get recommendations
        recommendation_query = f"""
        g.V().has('Order', 'id', 'Order_{order_id}')
         .inE('SERVES')
         .as('e')
         .outV()
         .project('carrier', 'details')
         .by(values('name'))
         .by(
             project('price', 'delivery_time', 'emissions', 'mode')
             .by(select('e').values('negotiated_price'))
             .by(select('e').values('delivery_time'))
             .by(values('co2_emissions'))
             .by(values('transport_mode'))
         )
         .dedup()
        """
        
        recommendations = execute_query(recommendation_query)
        carriers_processed = {}

        for rec in recommendations:
            carrier = rec['carrier']
            details = rec['details']
            
            recommendation = {
                "carrier": carrier,
                "price": float(details['price']),
                "delivery_time": details['delivery_time'],
                "emissions": f"{details['emissions']} kg CO2",
                "transport_mode": details['mode'],
                "hazmat_handling": "Certified" if is_hazmat else "Standard",
                "prime_benefits": "Applied" if is_prime else "N/A"
            }
            
            score = calculate_score(recommendation, is_hazmat, is_prime)
            recommendation["score"] = score
            
            # Add carrier-specific insights
            if carrier == "Maersk":
                recommendation.update({
                    "recommendation_type": "Most Eco-Friendly",
                    "strengths": ["Lowest emissions", "Cost-effective", "Reliable sea freight"],
                    "ideal_for": ["Non-urgent shipments", "Eco-conscious shipping"]
                })
            elif carrier == "GXO":
                recommendation.update({
                    "recommendation_type": "Balanced Choice",
                    "strengths": ["Good price-time ratio", "Moderate emissions"],
                    "ideal_for": ["Medium priority shipments", "Balanced needs"]
                })
            elif carrier == "FedEx":
                recommendation.update({
                    "recommendation_type": "Premium Balanced",
                    "strengths": ["Fast delivery", "Reliable tracking"],
                    "ideal_for": ["High-priority shipments", "Time-sensitive"]
                })
            elif carrier == "DHL":
                recommendation.update({
                    "recommendation_type": "Express Premium",
                    "strengths": ["Fastest delivery", "Priority handling"],
                    "ideal_for": ["Urgent deliveries", "Critical shipments"]
                })
            
            carriers_processed[carrier] = recommendation

        # Sort recommendations by score
        sorted_recommendations = sorted(
            carriers_processed.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        # Add position-based verdicts
        for i, rec in enumerate(sorted_recommendations):
            if i == 0:
                rec["verdict"] = f"Best Overall Option (Score: {rec['score']}%)"
                if is_hazmat:
                    rec["verdict"] += " for Hazardous Materials"
            else:
                position_verdicts = {
                    1: f"Strong Alternative (Score: {rec['score']}%)",
                    2: f"Viable Option (Score: {rec['score']}%)",
                    3: f"Premium Option (Score: {rec['score']}%)"
                }
                rec["verdict"] = position_verdicts.get(i, f"Additional Option (Score: {rec['score']}%)")

        # Close client connection
        gremlin_client.close()

        return {
            "status": "success",
            "message": "Processing completed successfully",
            "option_type_neptune": option_type_neptune,
            "recommendation_neptune": sorted_recommendations[:2]  # Top 2 recommendations
        }

    except Exception as e:
        print(f"Error: {e}")
        try:
            gremlin_client.close()
        except:
            pass
        return {"status": "error", "message": str(e)}